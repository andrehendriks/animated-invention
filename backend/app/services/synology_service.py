from pathlib import Path
import shutil

from app.models import StorageVolume


class SynologyService:
    """Inspect explicitly configured local mounts without accessing a NAS directly."""

    def __init__(self, mounts: dict[str, str]) -> None:
        self._mounts = mounts

    def list_volumes(self) -> list[StorageVolume]:
        volumes: list[StorageVolume] = []
        for name, configured_path in self._mounts.items():
            path = Path(configured_path).resolve(strict=True)
            if not path.is_dir():
                raise ValueError(f"Configured Synology mount '{name}' is not a directory")
            usage = shutil.disk_usage(path)
            volumes.append(
                StorageVolume(
                    name=name,
                    path=str(path),
                    total_bytes=usage.total,
                    used_bytes=usage.used,
                    free_bytes=usage.free,
                    usage_percent=round((usage.used / usage.total) * 100, 1) if usage.total else 0,
                )
            )
        return volumes
