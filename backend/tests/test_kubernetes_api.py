from fastapi.testclient import TestClient

import app.api.routes as routes_module
from app.main import app
from app.models import KubernetesPodLogs


def test_returns_selected_pod_logs(monkeypatch) -> None:
    async def fake_get_pod_logs(
        self, namespace: str, pod: str, tail: int
    ) -> KubernetesPodLogs:
        assert (namespace, pod, tail) == ("atlas", "api-7d6f9", 200)
        return KubernetesPodLogs(
            namespace=namespace,
            pod=pod,
            tail=tail,
            logs="service started",
        )

    monkeypatch.setattr(
        routes_module.KubernetesService, "get_pod_logs", fake_get_pod_logs
    )

    response = TestClient(app).get(
        "/api/kubernetes/namespaces/atlas/pods/api-7d6f9/logs?tail=200"
    )

    assert response.status_code == 200
    assert response.json() == {
        "namespace": "atlas",
        "pod": "api-7d6f9",
        "tail": 200,
        "logs": "service started",
    }


def test_rejects_invalid_pod_log_request() -> None:
    client = TestClient(app)

    assert client.get(
        "/api/kubernetes/namespaces/atlas/pods/invalid%3Bpod/logs"
    ).status_code == 422
    assert client.get(
        "/api/kubernetes/namespaces/atlas/pods/api-7d6f9/logs?tail=1001"
    ).status_code == 422
