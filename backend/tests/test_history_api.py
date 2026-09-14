import json
from types import SimpleNamespace

from fastapi.testclient import TestClient

import app.api.routes as routes_module
from app.main import app


class FakeOrchestrator:
    async def collect(self, message: str) -> list[str]:
        return [f"Evidence for: {message}"]


def test_persists_chat_response_in_history(monkeypatch, tmp_path) -> None:
    settings = SimpleNamespace(
        database_path=str(tmp_path / "atlas.db"),
        history_max_entries=1_000,
        ollama_model="test-model",
    )

    async def fake_chat(self, message: str) -> str:
        return f"Atlas response for: {message}"

    monkeypatch.setattr(routes_module, "get_settings", lambda: settings)
    monkeypatch.setattr(routes_module.OllamaService, "chat", fake_chat)
    monkeypatch.setattr(routes_module, "get_agent_orchestrator", FakeOrchestrator)

    client = TestClient(app)
    response = client.post("/api/chat", json={"message": "Check the API"})
    history = client.get("/api/history")

    assert response.status_code == 200
    assert history.status_code == 200
    assert history.json()[0]["category"] == "chat"
    assert history.json()[0]["request"] == "Check the API"
    assert json.loads(history.json()[0]["response"])["response"] == response.json()["response"]


def test_persists_incident_report_in_history(monkeypatch, tmp_path) -> None:
    settings = SimpleNamespace(
        database_path=str(tmp_path / "atlas.db"),
        history_max_entries=1_000,
    )

    monkeypatch.setattr(routes_module, "get_settings", lambda: settings)
    monkeypatch.setattr(routes_module, "get_agent_orchestrator", FakeOrchestrator)

    client = TestClient(app)
    response = client.post(
        "/api/incidents/analyze", json={"symptoms": "The radio is unavailable"}
    )
    history = client.get("/api/history")

    assert response.status_code == 200
    assert history.status_code == 200
    assert history.json()[0]["category"] == "incident"
    assert history.json()[0]["request"] == "The radio is unavailable"
    assert "root_cause" in history.json()[0]["response"]


def test_clears_history_via_api(monkeypatch, tmp_path) -> None:
    settings = SimpleNamespace(
        database_path=str(tmp_path / "atlas.db"),
        history_max_entries=1_000,
    )
    monkeypatch.setattr(routes_module, "get_settings", lambda: settings)
    history_service = routes_module.HistoryService(
        settings.database_path, settings.history_max_entries
    )
    history_service.record("chat", "first", "{}")

    response = TestClient(app).delete("/api/history")

    assert response.status_code == 200
    assert response.json() == {"deleted_entries": 1}
    assert history_service.list_entries(limit=10) == []
