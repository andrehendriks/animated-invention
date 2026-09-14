from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name: str
    keywords: set[str]

    @abstractmethod
    async def collect_evidence(self) -> list[str]:
        """Collect only safe, read-only evidence."""
