import httpx

from app.agents.base import BaseAgent
from app.services.command import CommandError
from app.services.docker_service import DockerService
from app.services.kubernetes_service import KubernetesService
from app.config import get_settings
from app.services.synology_service import SynologyService
from app.services.monitoring_service import MonitoringService
from app.services.github_service import GitHubService
from app.services.radio_service import RadioService
from app.services.backup_service import BackupService
from app.services.security_service import SecurityService
from app.services.automation_service import AutomationService


class DockerAgent(BaseAgent):
    name = "docker"
    keywords = {"docker", "container", "containers", "image", "cpu", "memory", "network"}

    async def collect_evidence(self) -> list[str]:
        try:
            containers = await DockerService().list_containers()
            stats = await DockerService().list_stats()
        except (CommandError, ValueError) as error:
            return [f"Docker diagnostics unavailable: {error}"]
        return [f"Docker reports {len(containers)} container(s) and resource data for {len(stats)} running container(s)."]


class KubernetesAgent(BaseAgent):
    name = "kubernetes"
    keywords = {"kubernetes", "k8s", "pod", "pods", "deployment", "cluster"}

    async def collect_evidence(self) -> list[str]:
        try:
            pods = await KubernetesService().list_pods()
            deployments = await KubernetesService().list_deployments()
            events = await KubernetesService().list_recent_events()
        except (CommandError, ValueError) as error:
            return [f"Kubernetes diagnostics unavailable: {error}"]
        degraded = sum(deployment.status == "degraded" for deployment in deployments)
        return [
            f"Kubernetes reports {len(pods)} pod(s), {len(deployments)} deployment(s), "
            f"{degraded} degraded deployment(s), and {len(events)} recent event(s)."
        ]


class SynologyAgent(BaseAgent):
    name = "synology"
    keywords = {"synology", "nas", "storage", "share", "mount", "smb", "nfs"}

    async def collect_evidence(self) -> list[str]:
        settings = get_settings()
        if not settings.synology_enabled:
            return ["Synology diagnostics are disabled."]
        try:
            volumes = SynologyService(settings.synology_mounts).list_volumes()
        except (OSError, ValueError) as error:
            return [f"Synology diagnostics unavailable: {error}"]
        return [
            f"Synology mount '{volume.name}' has {volume.free_bytes} free bytes "
            f"({volume.usage_percent}% used)."
            for volume in volumes
        ]


class MonitoringAgent(BaseAgent):
    name = "monitoring"
    keywords = {"monitoring", "metrics", "alert", "alerts", "prometheus", "cpu", "memory"}

    async def collect_evidence(self) -> list[str]:
        settings = get_settings()
        if not settings.monitoring_enabled:
            return ["Monitoring diagnostics are disabled."]
        try:
            alerts = await MonitoringService(settings.prometheus_base_url).list_alerts()
        except (httpx.HTTPError, ValueError) as error:
            return [f"Monitoring diagnostics unavailable: {error}"]
        firing = sum(alert.state == "firing" for alert in alerts)
        return [f"Prometheus reports {firing} firing alert(s) out of {len(alerts)} active alert(s)."]


class GitHubAgent(BaseAgent):
    name = "github"
    keywords = {"github", "repository", "repositories", "pull", "pr", "commit", "issue"}

    async def collect_evidence(self) -> list[str]:
        settings = get_settings()
        if not settings.github_enabled:
            return ["GitHub diagnostics are disabled."]
        try:
            pull_requests = await GitHubService(
                settings.github_repositories, settings.github_token
            ).list_open_pull_requests()
        except (httpx.HTTPError, ValueError) as error:
            return [f"GitHub diagnostics unavailable: {error}"]
        return [
            f"GitHub reports {len(pull_requests)} open pull request(s) across "
            f"{len(settings.github_repositories)} configured repository/repositories."
        ]


class RadioAgent(BaseAgent):
    name = "radio"
    keywords = {"radio", "stream", "streaming", "icecast", "liquidsoap", "playlist"}

    async def collect_evidence(self) -> list[str]:
        settings = get_settings()
        if not settings.radio_enabled:
            return ["Radio diagnostics are disabled."]
        try:
            radio = await RadioService(
                settings.icecast_status_url, settings.liquidsoap_health_url
            ).get_status()
        except (httpx.HTTPError, ValueError) as error:
            return [f"Radio diagnostics unavailable: {error}"]
        return [
            f"Icecast is healthy and reports {len(radio.mounts)} mountpoint(s) "
            f"with {sum(mount.listeners for mount in radio.mounts)} listener(s)."
        ]


class BackupAgent(BaseAgent):
    name = "backup"
    keywords = {"backup", "backups", "restore", "recovery", "snapshot"}

    async def collect_evidence(self) -> list[str]:
        settings = get_settings()
        if not settings.backup_enabled:
            return ["Backup diagnostics are disabled."]
        try:
            backup = BackupService(settings.backup_path).get_status()
        except (OSError, ValueError) as error:
            return [f"Backup diagnostics unavailable: {error}"]
        newest = backup.newest_backup or "no backup files"
        return [f"Backup inventory has {backup.file_count} file(s); newest entry: {newest}."]


class SecurityAgent(BaseAgent):
    name = "security"
    keywords = {"security", "secure", "authentication", "auth", "cors", "exposure"}

    async def collect_evidence(self) -> list[str]:
        findings = SecurityService(get_settings()).assess()
        high_count = sum(finding.severity == "high" for finding in findings)
        return [f"Atlas configuration assessment found {high_count} high-severity item(s) and {len(findings)} finding(s) total."]


class AutomationAgent(BaseAgent):
    name = "automation"
    keywords = {"automate", "automation", "remediate", "remediation", "self-healing"}

    async def collect_evidence(self) -> list[str]:
        return ["Automation is configured in observe-only mode; no actions can be executed."]


class LogAgent(BaseAgent):
    name = "logs"
    keywords = {"log", "logs", "error", "errors", "traceback", "exception"}

    async def collect_evidence(self) -> list[str]:
        return ["No raw logs were supplied to the chat request; submit them through the log analysis endpoint for evidence."]
