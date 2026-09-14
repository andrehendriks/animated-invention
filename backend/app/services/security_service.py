from app.config import Settings
from app.models import SecurityFinding


class SecurityService:
    """Assess Atlas configuration without probing external systems or secrets."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def assess(self) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        if not self._settings.auth_enabled:
            findings.append(
                SecurityFinding(
                    severity="high",
                    category="authentication",
                    message="API-key authentication is disabled.",
                    remediation="Enable ATLAS_AUTH_ENABLED before exposing Atlas outside a trusted network.",
                )
            )
        elif len(self._settings.api_key) < 32:
            findings.append(
                SecurityFinding(
                    severity="high",
                    category="authentication",
                    message="The configured API key is shorter than 32 characters.",
                    remediation="Replace it with a unique, randomly generated key of at least 32 characters.",
                )
            )
        if "*" in self._settings.allowed_origins:
            findings.append(
                SecurityFinding(
                    severity="high",
                    category="cors",
                    message="CORS permits requests from every origin.",
                    remediation="Set ATLAS_ALLOWED_ORIGINS to the exact trusted UI origins.",
                )
            )
        if self._settings.docker_enabled:
            findings.append(
                SecurityFinding(
                    severity="medium",
                    category="integration",
                    message="Docker diagnostics are enabled and may require Docker socket access.",
                    remediation="Mount the socket only on trusted hosts and keep Atlas access read-only.",
                )
            )
        if self._settings.github_enabled and not self._settings.github_token:
            findings.append(
                SecurityFinding(
                    severity="low",
                    category="integration",
                    message="GitHub integration has no token and can inspect public repositories only.",
                    remediation="Use a fine-grained read-only token if private repository access is required.",
                )
            )
        return findings
