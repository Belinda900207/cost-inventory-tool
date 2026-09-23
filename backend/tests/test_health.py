from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_a_known_status() -> None:
    response = client.get("/health")

    assert response.status_code in {200, 503}
    assert response.json()["status"] in {"ok", "unhealthy"}
