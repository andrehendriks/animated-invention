from types import SimpleNamespace

from fastapi.testclient import TestClient

import app.dependencies as dependencies_module
import app.api.routes as routes_module
from app.main import app


def test_health_returns_configured_integrations() -> None:
    response = TestClient(app).get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert {item["name"] for item in response.json()["services"]} == {
        "api",
        "docker",
        "kubernetes",
        "synology",
        "monitoring",
        "github",
        "radio",
        "backup",
        "security",
        "automation",
        "log-analysis",
        "incident-analysis",
    }


def test_probe_routes_remain_public_when_api_key_authentication_is_enabled(monkeypatch) -> None:
    async def fake_check_ready(self) -> None:
        return None

    monkeypatch.setattr(
        dependencies_module,
        "get_settings",
        lambda: SimpleNamespace(auth_enabled=True, api_key="test-key"),
    )
    monkeypatch.setattr(routes_module.OllamaService, "check_ready", fake_check_ready)

    client = TestClient(app)

    assert client.get("/api/health").status_code == 200
    assert client.get("/api/ready").status_code == 200
    assert client.get("/api/security/posture").status_code == 401
    assert client.get(
        "/api/security/posture", headers={"X-API-Key": "test-key"}
    ).status_code == 200
