"""Opt-in inventory persistence test for the isolated cost-inventory-test DB."""

import os
import subprocess
import sys
from uuid import uuid4

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app import db
from app.config import Settings
from app.main import create_app
from tests.integration.test_mysql import ROOT

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MYSQL_INTEGRATION") != "1", reason="opt-in isolated MySQL test"
)


def test_inventory_migration_persistence_constraints_and_reconnect(monkeypatch):
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
    name = f"Product A {uuid4().hex}"
    app = create_app()
    try:
        with TestClient(app) as client:
            product = client.post("/api/v1/products", json={"name": name})
            assert product.status_code == 201
            product_id = product.json()["product_id"]
            duplicate = client.post(
                "/api/v1/products", json={"name": f"  {name.upper()}  "}
            )
            assert duplicate.status_code == 409

            for quantity, cost, purchased_at in [
                (20, "80.000000", "2026-09-27T01:00:00Z"),
                (10, "100.000000", "2026-09-28T01:00:00Z"),
            ]:
                response = client.post(
                    "/api/v1/purchase-batches",
                    json={
                        "product_id": product_id,
                        "quantity": quantity,
                        "unit_cost": cost,
                        "currency": "CAD",
                        "purchased_at": purchased_at,
                    },
                )
                assert response.status_code == 201

            inventory = client.get(f"/api/v1/inventory/{product_id}")
            assert inventory.status_code == 200
            assert inventory.json()["total_remaining_quantity"] == 30
            assert [
                item["remaining_quantity"] for item in inventory.json()["batches"]
            ] == [20, 10]

            db.get_engine().dispose()
            persisted = client.get(f"/api/v1/inventory/{product_id}")
            assert persisted.status_code == 200
            assert persisted.json()["total_remaining_quantity"] == 30

            invalid_rows = [
                {"original": 0, "remaining": 0, "cost": "80.000000", "currency": "CAD"},
                {"original": 1, "remaining": 1, "cost": "0", "currency": "CAD"},
                {"original": 1, "remaining": 1, "cost": "80.000000", "currency": "USD"},
                {"original": 1, "remaining": 2, "cost": "80.000000", "currency": "CAD"},
            ]
            for row in invalid_rows:
                with pytest.raises(IntegrityError):
                    with db.get_engine().begin() as connection:
                        connection.execute(
                            text(
                                "INSERT INTO purchase_batches "
                                "(product_id, original_quantity, remaining_quantity, "
                                "unit_cost, currency, purchased_at) "
                                "VALUES (:product_id, :original, :remaining, :cost, "
                                ":currency, CURRENT_TIMESTAMP(6))"
                            ),
                            {"product_id": product_id, **row},
                        )

            for payload in [
                {"quantity": 0, "unit_cost": "80.00", "currency": "CAD"},
                {"quantity": -1, "unit_cost": "80.00", "currency": "CAD"},
                {"quantity": 1, "unit_cost": "0", "currency": "CAD"},
                {"quantity": 1, "unit_cost": "80.00", "currency": "USD"},
            ]:
                response = client.post(
                    "/api/v1/purchase-batches",
                    json={
                        "product_id": product_id,
                        "purchased_at": "2026-09-28T01:00:00Z",
                        **payload,
                    },
                )
                assert response.status_code == 422
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
