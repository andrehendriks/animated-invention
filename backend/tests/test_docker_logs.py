import asyncio

import pytest

import app.services.docker_service as docker_module
from app.services.command import CommandResult
from app.services.docker_service import DockerService


def test_reads_bounded_container_logs(monkeypatch) -> None:
    async def fake_command(*command: str, timeout: int = 15) -> CommandResult:
        assert command == ("docker", "logs", "--tail", "200", "atlas")
        return CommandResult(stdout="started", stderr="", return_code=0)

    monkeypatch.setattr(docker_module, "run_read_only_command", fake_command)

    logs = asyncio.run(DockerService().get_logs("atlas", 200))

    assert logs.logs == "started"


def test_rejects_invalid_container_identifier() -> None:
    with pytest.raises(ValueError, match="invalid format"):
        asyncio.run(DockerService().get_logs("atlas; rm -rf /", 200))
