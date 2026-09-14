from datetime import datetime, timezone
from pathlib import Path

from app.models import BackupStatus


class BackupService:
    """Inspect a configured backup directory without reading or changing its contents."""

    def __init__(self, backup_path: str) -> None:
        self._backup_path = Path(backup_path)

    def get_status(self) -> BackupStatus:
        path = self._backup_path.resolve(strict=True)
        if not path.is_dir():
            raise ValueError("Configured backup path is not a directory")
        files = [item for item in path.iterdir() if item.is_file()]
        newest = max(files, key=lambda item: item.stat().st_mtime, default=None)
        return BackupStatus(
            path=str(path),
            file_count=len(files),
            total_bytes=sum(item.stat().st_size for item in files),
            newest_backup=newest.name if newest else None,
            newest_backup_at=(
                datetime.fromtimestamp(newest.stat().st_mtime, tz=timezone.utc).isoformat()
                if newest
                else None
            ),
        )
