
from fastapi.testclient import TestClient

from datapilot.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Verify the API health endpoint returns the expected response."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "DataPilot",
    }
