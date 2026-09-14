from fastapi.testclient import TestClient

import app.api.routes as routes_module
from app.main import app


def test_reports_ready_when_ollama_is_available(monkeypatch) -> None:
    async def fake_check_ready(self) -> None:
        return None

    monkeypatch.setattr(routes_module.OllamaService, "check_ready", fake_check_ready)

    response = TestClient(app).get("/api/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "ollama": "available"}


def test_reports_unready_when_ollama_is_unavailable(monkeypatch) -> None:
    async def fake_check_ready(self) -> None:
        raise routes_module.httpx.ConnectError("Connection refused")

    monkeypatch.setattr(routes_module.OllamaService, "check_ready", fake_check_ready)

    response = TestClient(app).get("/api/ready")

    assert response.status_code == 503
    assert response.json()["detail"] == "Ollama is unavailable"
