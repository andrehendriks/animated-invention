from app.services.log_service import LogService


def test_groups_connection_errors_and_preserves_timestamps() -> None:
    analysis = LogService().analyze(
        "2026-09-14 08:00:00 ERROR ECONNREFUSED icecast\n"
        "2026-09-14 08:01:00 ERROR connection refused icecast\n"
    )

    assert analysis.issues[0].category == "Connection refused"
    assert analysis.issues[0].count == 2
    assert analysis.issues[0].first_timestamp == "2026-09-14 08:00:00"
