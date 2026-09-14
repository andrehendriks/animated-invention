from app.services.automation_service import AutomationService


def test_crash_plan_requires_logs_and_human_approval() -> None:
    plan = AutomationService().plan("A container keeps crashing")

    assert plan.execution_mode == "observe-only"
    assert "Collect recent service logs." in plan.evidence_required
    assert any("human approval" in action for action in plan.proposed_actions)
