from app.services.history_service import HistoryService


def test_persists_and_orders_local_history(tmp_path) -> None:
    service = HistoryService(str(tmp_path / "atlas.db"))
    first = service.record("chat", "Which pod is unhealthy?", '{"response":"api"}')
    second = service.record("incident", "Radio unavailable", '{"root_cause":"Undetermined"}')

    entries = service.list_entries(limit=10)

    assert [entry.id for entry in entries] == [second.id, first.id]
    assert entries[0].category == "incident"
    assert entries[1].request == "Which pod is unhealthy?"


def test_prunes_oldest_records_when_retention_limit_is_reached(tmp_path) -> None:
    service = HistoryService(str(tmp_path / "atlas.db"), max_entries=2)
    first = service.record("chat", "first", "{}")
    service.record("chat", "second", "{}")
    third = service.record("incident", "third", "{}")

    entries = service.list_entries(limit=10)

    assert [entry.id for entry in entries] == [third.id, first.id + 1]


def test_clears_local_history(tmp_path) -> None:
    service = HistoryService(str(tmp_path / "atlas.db"))
    service.record("chat", "first", "{}")
    service.record("incident", "second", "{}")

    deleted_entries = service.clear()

    assert deleted_entries == 2
    assert service.list_entries(limit=10) == []
