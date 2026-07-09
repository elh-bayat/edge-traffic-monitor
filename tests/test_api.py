import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


def get_client():
    with patch('main.rabbitmq_channel', new=AsyncMock()):
        from main import app
        return TestClient(app)


def test_health_check():
    client = get_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_invalid_vehicle_count():
    client = get_client()
    payload = {
        "camera_id": "cam_01",
        "location": "Street A",
        "timestamp": "2026-07-01T10:00:00Z",
        "vehicle_count": -5,
        "average_speed_kmh": 60.0,
        "weather": "clear"
    }
    response = client.post("/api/v1/traffic", json=payload)
    assert response.status_code == 422
