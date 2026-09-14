from app.services.incident_service import IncidentService


def test_keeps_root_cause_undetermined_when_evidence_is_not_causal() -> None:
    report = IncidentService().analyze("The radio stream is offline", ["Icecast is unavailable."])

    assert report.root_cause.startswith("Undetermined")
    assert report.confidence_percent == 10
    assert report.remediation
