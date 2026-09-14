import asyncio

import app.services.docker_service as docker_module
from app.services.command import CommandResult
from app.services.docker_service import DockerService


def test_parses_non_streaming_docker_stats(monkeypatch) -> None:
    async def fake_command(*command: str, timeout: int = 15) -> CommandResult:
        return CommandResult(
            stdout='{"Name":"atlas","ID":"abc123","CPUPerc":"1.2%","MemUsage":"20MiB / 1GiB","MemPerc":"2%","NetIO":"2kB / 3kB"}',
            stderr="",
            return_code=0,
        )

    monkeypatch.setattr(docker_module, "run_read_only_command", fake_command)

    stats = asyncio.run(DockerService().list_stats())

    assert stats[0].name == "atlas"
    assert stats[0].cpu_percent == "1.2%"
