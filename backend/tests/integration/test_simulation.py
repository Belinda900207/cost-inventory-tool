"""Opt-in proof that cost simulations never mutate the isolated MySQL database."""

import os
import subprocess
import sys
from uuid import uuid4

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import text

from app import db
from app.config import Settings
from app.main import create_app
from tests.integration.test_mysql import ROOT

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MYSQL_INTEGRATION") != "1", reason="opt-in isolated MySQL test"
)


def test_repeated_simulation_preserves_all_inventory_rows(monkeypatch):
    values = dotenv_values(ROOT / ".env.test")
    assert values["MYSQL_DATABASE"] == "cost_inventory_test"
    assert values["MYSQL_USER"] == "test_app"
    assert values["MYSQL_PORT"] == "3307"
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    settings = Settings(_env_file=None)
    monkeypatch.setattr(db, "get_settings", lambda: settings)
    db.get_engine.cache_clear()

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT / "backend",
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, "alembic upgrade head failed (details withheld)"

    product_id = None
    app = create_app()
    try:
        with TestClient(app) as client:
            product = client.post(
                "/api/v1/products", json={"name": f"Simulation {uuid4().hex}"}
            )
            assert product.status_code == 201
            product_id = product.json()["product_id"]
            for quantity, cost, purchased_at in [
                (20, "80.000000", "2026-09-27T01:00:00Z"),
                (10, "100.000000", "2026-09-28T01:00:00Z"),
            ]:
                created = client.post(
                    "/api/v1/purchase-batches",
                    json={
                        "product_id": product_id,
                        "quantity": quantity,
                        "unit_cost": cost,
                        "currency": "CAD",
                        "purchased_at": purchased_at,
                    },
                )
                assert created.status_code == 201

            engine = db.get_engine()
            snapshot_sql = text(
                "SELECT id, product_id, original_quantity, remaining_quantity, "
                "unit_cost, currency, purchased_at, created_at, updated_at "
                "FROM purchase_batches WHERE product_id = :product_id ORDER BY id"
            )
            with engine.connect() as connection:
                before = list(
                    connection.execute(
                        snapshot_sql, {"product_id": product_id}
                    ).tuples()
                )

            payload = {
                "product_id": product_id,
                "quantity": 25,
                "selling_unit_price": "120.00",
                "currency": "CAD",
            }
            responses = [
                client.post("/api/v1/simulations/cost", json=payload) for _ in range(10)
            ]
            assert all(response.status_code == 200 for response in responses)
            assert all(response.json() == responses[0].json() for response in responses)

            exact = client.post(
                "/api/v1/simulations/cost", json={**payload, "quantity": 30}
            )
            insufficient = client.post(
                "/api/v1/simulations/cost", json={**payload, "quantity": 31}
            )
            assert exact.status_code == 200
            assert insufficient.status_code == 409

            with engine.connect() as connection:
                after = list(
                    connection.execute(
                        snapshot_sql, {"product_id": product_id}
                    ).tuples()
                )
                business_tables = set(
                    connection.execute(
                        text(
                            "SELECT table_name FROM information_schema.tables "
                            "WHERE table_schema = DATABASE()"
                        )
                    ).scalars()
                )

            assert after == before
            assert business_tables == {
                "alembic_version",
                "products",
                "purchase_batches",
            }
    finally:
        engine = db.get_engine()
        if product_id is not None:
            with engine.begin() as connection:
                connection.execute(
                    text("DELETE FROM purchase_batches WHERE product_id = :product_id"),
                    {"product_id": product_id},
                )
                connection.execute(
                    text("DELETE FROM products WHERE id = :product_id"),
                    {"product_id": product_id},
                )
        engine.dispose()
        db.get_engine.cache_clear()
