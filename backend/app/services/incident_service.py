from app.models import IncidentAnalysis
from app.services.automation_service import AutomationService


class IncidentService:
    """Create an evidence-bound incident report without fabricating a root cause."""

    def analyze(self, symptoms: str, evidence: list[str]) -> IncidentAnalysis:
        confidence = 0 if not evidence else 20
        if any("unavailable" in item.lower() or "disabled" in item.lower() for item in evidence):
            confidence = min(confidence, 10)
        return IncidentAnalysis(
            symptoms=symptoms,
            evidence=evidence,
            root_cause=(
                "Undetermined: the collected evidence does not yet establish a causal chain."
                if evidence
                else "Undetermined: no diagnostic evidence was collected for the reported symptoms."
            ),
            impact="Impact requires operator assessment from the affected service state.",
            remediation=AutomationService().plan(symptoms).proposed_actions,
            confidence_percent=confidence,
        )
