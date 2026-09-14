from app.config import Settings
from app.services.security_service import SecurityService


def test_reports_disabled_authentication() -> None:
    findings = SecurityService(Settings()).assess()

    assert any(finding.category == "authentication" and finding.severity == "high" for finding in findings)
