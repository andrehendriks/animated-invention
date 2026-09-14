from fastapi.testclient import TestClient

from app.main import app


def test_exposes_prometheus_metrics() -> None:
    response = TestClient(app).get("/metrics")

    assert response.status_code == 200
    assert "python_info" in response.text
