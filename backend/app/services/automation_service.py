from app.models import AutomationPlan


class AutomationService:
    """Produce deterministic remediation plans without performing actions."""

    def plan(self, objective: str) -> AutomationPlan:
        normalized = objective.lower()
        evidence = ["Confirm the affected service and its current health state."]
        actions = ["Document the diagnosis and request human approval before any change."]

        if any(term in normalized for term in ("crash", "restart", "unhealthy", "offline")):
            evidence.extend(["Collect recent service logs.", "Inspect dependency and platform events."])
            actions.insert(0, "Propose a targeted service restart after evidence confirms the failure.")
        elif any(term in normalized for term in ("disk", "storage", "space", "volume")):
            evidence.extend(["Inspect volume capacity.", "Identify the largest recent data sources."])
            actions.insert(0, "Propose storage cleanup or capacity expansion for human review.")
        elif any(term in normalized for term in ("backup", "restore", "recovery")):
            evidence.extend(["Inspect backup inventory.", "Verify the most recent backup timestamp."])
            actions.insert(0, "Propose a non-production restore verification for human review.")

        return AutomationPlan(
            objective=objective,
            evidence_required=evidence,
            proposed_actions=actions,
        )
