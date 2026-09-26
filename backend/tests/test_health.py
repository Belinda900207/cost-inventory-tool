from collections.abc import Iterator
from types import ModuleType
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def health_client(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[TestClient, ModuleType]]:
    # app.config builds an engine on import. These values are never used to connect.
    monkeypatch.setenv("MYSQL_DATABASE", "test_only")
    monkeypatch.setenv("MYSQL_USER", "test_user")
    monkeypatch.setenv("MYSQL_PASSWORD", "unused_test_password")

    from app import main

    with TestClient(main.app) as client:
        yield client, main


def test_health_returns_ok_when_database_check_succeeds(
    health_client: tuple[TestClient, ModuleType], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, main = health_client
    check = Mock()
    monkeypatch.setattr(main, "check_database", check)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
    check.assert_called_once_with()


def test_health_returns_503_without_leaking_database_error(
    health_client: tuple[TestClient, ModuleType], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, main = health_client
    check = Mock(side_effect=RuntimeError("private database connection detail"))
    monkeypatch.setattr(main, "check_database", check)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy", "database": "unavailable"}
    assert "private database connection detail" not in response.text
    check.assert_called_once_with()
