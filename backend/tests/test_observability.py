import json
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.main import create_app


@pytest.mark.parametrize("value", ["", "bad id", "x" * 65, "bad\nline"])
def test_invalid_id_is_replaced(value):
    with TestClient(create_app()) as client:
        response = client.get("/health/live", headers={"X-Request-ID": value})
    UUID(response.headers["x-request-id"])
    assert response.headers["x-request-id"] != value


def test_valid_id_and_safe_structured_log(caplog):
    with TestClient(create_app()) as client:
        response = client.get(
            "/health/live?password=hidden", headers={"X-Request-ID": "trace_123-A"}
        )
    assert response.headers["x-request-id"] == "trace_123-A"
    records = [
        json.loads(r.message)
        for r in caplog.records
        if r.name == "cost_inventory.requests"
    ]
    record = records[-1]
    assert record["request_id"] == "trace_123-A"
    assert record["path"] == "/health/live"
    assert record["status"] == 200
    assert record["duration_ms"] >= 0
    assert {
        "time",
        "level",
        "service",
        "environment",
        "method",
        "message",
    } <= record.keys()
    assert "hidden" not in json.dumps(records)


def test_safe_errors_and_ids(caplog):
    app = create_app()

    @app.get("/explode")
    def explode():
        raise RuntimeError("private-password-and-db-url")

    class Payload(BaseModel):
        count: int

    @app.post("/validate")
    def validate(payload: Payload):
        return payload

    with TestClient(app) as client:
        for method, path, kwargs, expected in [
            ("GET", "/explode", {}, 500),
            ("GET", "/private-password-and-db-url", {}, 404),
            (
                "POST",
                "/validate",
                {"json": {"count": "private-password-and-db-url"}},
                422,
            ),
            ("POST", "/health/live", {}, 405),
        ]:
            response = client.request(method, path, **kwargs)
            assert response.status_code == expected
            assert (
                response.json()["error"]["request_id"]
                == response.headers["x-request-id"]
            )
            assert "private-password" not in response.text
    logs = [r.message for r in caplog.records if r.name == "cost_inventory.requests"]
    assert "private-password" not in str(logs)


def test_generated_ids_are_unique_and_duplicate_headers_rejected():
    with TestClient(create_app()) as client:
        first = client.get("/health/live")
        second = client.get(
            "/health/live", headers=[("X-Request-ID", "one"), ("X-Request-ID", "two")]
        )
    assert first.headers["x-request-id"] != second.headers["x-request-id"]
    UUID(second.headers["x-request-id"])
