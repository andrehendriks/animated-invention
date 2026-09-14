import json
import re

from app.services.command import run_read_only_command
from app.models import DockerContainerLogs, DockerContainerStats

CONTAINER_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


class DockerService:
    async def list_containers(self) -> list[dict[str, str]]:
        result = await run_read_only_command(
            "docker", "ps", "--format", "{{json .}}", "--all"
        )
        return [json.loads(line) for line in result.stdout.splitlines() if line]

    async def list_stats(self) -> list[DockerContainerStats]:
        result = await run_read_only_command(
            "docker", "stats", "--no-stream", "--format", "{{json .}}"
        )
        return [
            DockerContainerStats(
                name=item.get("Name", "unknown"),
                container_id=item.get("ID", ""),
                cpu_percent=item.get("CPUPerc", "N/A"),
                memory_usage=item.get("MemUsage", "N/A"),
                memory_percent=item.get("MemPerc", "N/A"),
                network_io=item.get("NetIO", "N/A"),
            )
            for line in result.stdout.splitlines()
            if line
            for item in [json.loads(line)]
        ]

    async def get_logs(self, container: str, tail: int) -> DockerContainerLogs:
        if not CONTAINER_IDENTIFIER_PATTERN.fullmatch(container):
            raise ValueError("Container identifier has an invalid format")
        result = await run_read_only_command("docker", "logs", "--tail", str(tail), container)
        logs = "\n".join(part for part in (result.stdout, result.stderr) if part)[-100_000:]
        return DockerContainerLogs(container=container, tail=tail, logs=logs)
