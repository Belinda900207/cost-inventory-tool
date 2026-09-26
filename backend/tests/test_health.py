from collections.abc import Iterator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.db import get_database_check
from app.main import create_app


@pytest.fixture
def health_client() -> Iterator[tuple[TestClient, Mock]]:
    app = create_app()
    check = Mock()
    app.dependency_overrides[get_database_check] = lambda: check
    with TestClient(app) as client:
        yield client, check


@pytest.mark.parametrize("path", ["/health", "/health/ready"])
def test_health_success(health_client: tuple[TestClient, Mock], path: str) -> None:
    client, check = health_client
    response = client.get(path)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
    check.assert_called_once_with()


@pytest.mark.parametrize("path", ["/health", "/health/ready"])
def test_health_safe_failure(health_client: tuple[TestClient, Mock], path: str) -> None:
    client, check = health_client
    check.side_effect = RuntimeError("private database connection detail")
    response = client.get(path)
    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy", "database": "unavailable"}
    assert "private" not in response.text
    check.assert_called_once_with()


def test_live_never_calls_database(health_client: tuple[TestClient, Mock]) -> None:
    client, check = health_client
    check.side_effect = RuntimeError("database unavailable")
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    check.assert_not_called()
