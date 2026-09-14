from pathlib import Path

from app.services.backup_service import BackupService


def test_reports_direct_backup_files(tmp_path: Path) -> None:
    (tmp_path / "atlas-2026-09-14.tar.gz").write_bytes(b"backup-data")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "ignored.txt").write_text("not included")

    status = BackupService(str(tmp_path)).get_status()

    assert status.file_count == 1
    assert status.total_bytes == len(b"backup-data")
    assert status.newest_backup == "atlas-2026-09-14.tar.gz"
