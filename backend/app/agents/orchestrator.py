import re

from app.agents.base import BaseAgent


class AgentOrchestrator:
    """Select relevant diagnostic agents from a deliberately small plugin registry."""

    def __init__(self, agents: list[BaseAgent]) -> None:
        self._agents = agents

    async def collect(self, message: str) -> list[str]:
        words = set(re.findall(r"\w+", message.lower()))
        selected = [agent for agent in self._agents if agent.keywords & words]
        evidence: list[str] = []
        for agent in selected:
            evidence.extend(await agent.collect_evidence())
        return evidence
