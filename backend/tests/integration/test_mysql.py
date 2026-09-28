"""Opt-in: only the fixed cost-inventory-test Compose project may be stopped."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import text

from app import db
from app.config import Settings
from app.main import create_app

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MYSQL_INTEGRATION") != "1", reason="opt-in isolated MySQL test"
)
ROOT = Path(__file__).resolve().parents[3]
COMPOSE = [
    "docker",
    "compose",
    "--env-file",
    str(ROOT / ".env.test"),
    "-p",
    "cost-inventory-test",
    "-f",
    str(ROOT / "compose.test.yaml"),
]


def compose(*args):
    subprocess.run(COMPOSE + list(args), check=True, cwd=ROOT, timeout=180)


def test_real_mysql_readiness_restart_and_outage(monkeypatch):
    values = dotenv_values(ROOT / ".env.test")
    # Explicit assertions prevent any accidental use of development settings.
    assert values["MYSQL_DATABASE"] == "cost_inventory_test"
    assert values["MYSQL_USER"] == "test_app"
    assert values["MYSQL_HOST"] == "127.0.0.1"
    assert values["MYSQL_PORT"] == "3307"
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    settings = Settings(_env_file=None)
    monkeypatch.setattr(db, "get_settings", lambda: settings)
    db.get_engine.cache_clear()
    engine = db.get_engine()
    try:
        compose("up", "-d", "--wait", "--wait-timeout", "150")
        with engine.connect() as connection:
            version, database, user, server_uuid = connection.execute(
                text("SELECT VERSION(), DATABASE(), CURRENT_USER(), @@server_uuid")
            ).one()
            assert version.startswith("8.4.")
            assert database == "cost_inventory_test"
            assert user.startswith("test_app@")
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "current"],
            cwd=ROOT / "backend",
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == 0, "alembic current failed (details withheld)"
        print("alembic current connected successfully; revision state inspected")
        with TestClient(create_app()) as client:
            assert client.get("/health/ready").status_code == 200
            compose("restart", "db")
            compose("up", "-d", "--wait", "--wait-timeout", "150")
            engine.dispose()
            with engine.connect() as connection:
                assert connection.scalar(text("SELECT @@server_uuid")) == server_uuid
            assert client.get("/health/ready").status_code == 200
            compose("stop", "db")
            assert client.get("/health/live").status_code == 200
            response = client.get("/health/ready")
            assert response.status_code == 503
            assert response.json()["error"]["code"] == "database_unavailable"
            assert (
                response.json()["error"]["request_id"]
                == response.headers["x-request-id"]
            )
            assert values["MYSQL_PASSWORD"] not in response.text
            compose("up", "-d", "--wait", "--wait-timeout", "150")
            assert client.get("/health/ready").status_code == 200
        print(
            "MySQL 8.4 app SELECT 1, persistent server UUID, outage and recovery verified"
        )
    finally:
        engine.dispose()
        db.get_engine.cache_clear()
        compose("up", "-d", "--wait", "--wait-timeout", "150")
