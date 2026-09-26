import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from app.auth.dependencies import require_principal
from app.auth.schemas import LoginRequest
from app.main import create_app


def test_auth_routes_do_not_claim_to_exist():
    with TestClient(create_app()) as client:
        assert client.post("/api/v1/auth/login", json={}).status_code == 404
        assert client.get("/api/v1/auth/me").status_code == 404


def test_unconfigured_auth_fails_closed():
    app = create_app()

    @app.get("/protected-test", dependencies=[Depends(require_principal)])
    def protected():
        pytest.fail("An unconfigured auth service must never permit this handler")

    with TestClient(app) as client:
        response = client.get("/protected-test")
        assert response.status_code == 501
        assert response.json()["error"]["code"] == "http_error"


def test_auth_input_repr_hides_secret():
    credentials = LoginRequest(
        identifier="test-placeholder", password="not-a-real-password"
    )
    assert "not-a-real-password" not in repr(credentials)
