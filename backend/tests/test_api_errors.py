from types import SimpleNamespace

from fastapi.testclient import TestClient

import app.api.routes as routes_module
from app.main import app
from app.services.command import CommandError
from app.services.history_service import HistoryService


class FakeOrchestrator:
    async def collect(self, message: str) -> list[str]:
        return [f"Evidence for: {message}"]


def test_chat_returns_service_unavailable_without_recording_history(
    monkeypatch, tmp_path
) -> None:
    settings = SimpleNamespace(
        database_path=str(tmp_path / "atlas.db"),
        history_max_entries=1_000,
        ollama_model="test-model",
    )

    async def fake_chat(self, message: str) -> str:
        raise routes_module.httpx.ConnectError("Connection refused")

    monkeypatch.setattr(routes_module, "get_settings", lambda: settings)
    monkeypatch.setattr(routes_module, "get_agent_orchestrator", FakeOrchestrator)
    monkeypatch.setattr(routes_module.OllamaService, "chat", fake_chat)

    client = TestClient(app)
    response = client.post("/api/chat", json={"message": "Check the API"})

    assert response.status_code == 503
    assert response.json() == {"detail": "Ollama is unavailable"}
    assert HistoryService(settings.database_path, settings.history_max_entries).list_entries(
        limit=10
    ) == []


def test_docker_logs_returns_service_unavailable_when_command_fails(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        routes_module,
        "get_settings",
        lambda: SimpleNamespace(docker_enabled=True),
    )

    async def fake_get_logs(self, container: str, tail: int):
        raise CommandError(f"Unable to read logs for {container} ({tail})")

    monkeypatch.setattr(routes_module.DockerService, "get_logs", fake_get_logs)

    response = TestClient(app).get("/api/docker/containers/atlas/logs?tail=25")

    assert response.status_code == 503
    assert response.json() == {"detail": "Unable to read logs for atlas (25)"}
