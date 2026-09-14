from app.agents.diagnostic_agents import (
    AutomationAgent,
    BackupAgent,
    DockerAgent,
    GitHubAgent,
    KubernetesAgent,
    LogAgent,
    MonitoringAgent,
    RadioAgent,
    SecurityAgent,
    SynologyAgent,
)
from app.agents.orchestrator import AgentOrchestrator


def get_agent_orchestrator() -> AgentOrchestrator:
    return AgentOrchestrator([
        DockerAgent(),
        KubernetesAgent(),
        SynologyAgent(),
        MonitoringAgent(),
        GitHubAgent(),
        RadioAgent(),
        BackupAgent(),
        SecurityAgent(),
        AutomationAgent(),
        LogAgent(),
    ])
