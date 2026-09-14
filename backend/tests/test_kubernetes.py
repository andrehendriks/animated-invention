import asyncio
import json

import pytest

import app.services.kubernetes_service as kubernetes_module
from app.services.command import CommandResult
from app.services.kubernetes_service import KubernetesService


def test_reports_degraded_deployment(monkeypatch) -> None:
    async def fake_command(*command: str, timeout: int = 15) -> CommandResult:
        return CommandResult(
            stdout=json.dumps({"items": [{
                "metadata": {"name": "radio", "namespace": "media"},
                "spec": {"replicas": 2},
                "status": {"availableReplicas": 1},
            }]}),
            stderr="",
            return_code=0,
        )

    monkeypatch.setattr(kubernetes_module, "run_read_only_command", fake_command)

    deployment = asyncio.run(KubernetesService().list_deployments())[0]

    assert deployment.status == "degraded"
    assert deployment.available_replicas == 1


def test_limits_recent_events(monkeypatch) -> None:
    async def fake_command(*command: str, timeout: int = 15) -> CommandResult:
        return CommandResult(
            stdout=json.dumps({"items": [
                {"metadata": {"namespace": "atlas", "creationTimestamp": "2026-09-14T08:00:00Z"}, "involvedObject": {"name": f"pod-{index}"}, "reason": "Started"}
                for index in range(3)
            ]}),
            stderr="",
            return_code=0,
        )

    monkeypatch.setattr(kubernetes_module, "run_read_only_command", fake_command)

    events = asyncio.run(KubernetesService().list_recent_events(limit=2))

    assert [event.involved_object for event in events] == ["pod-1", "pod-2"]


def test_reads_bounded_pod_logs(monkeypatch) -> None:
    async def fake_command(*command: str, timeout: int = 15) -> CommandResult:
        assert command == ("kubectl", "logs", "--namespace", "atlas", "--tail", "200", "api-7d6f9")
        return CommandResult(stdout="started", stderr="", return_code=0)

    monkeypatch.setattr(kubernetes_module, "run_read_only_command", fake_command)

    logs = asyncio.run(KubernetesService().get_pod_logs("atlas", "api-7d6f9", 200))

    assert logs.logs == "started"


def test_rejects_invalid_pod_identifier() -> None:
    with pytest.raises(ValueError, match="invalid format"):
        asyncio.run(KubernetesService().get_pod_logs("atlas", "api; rm -rf /", 200))
