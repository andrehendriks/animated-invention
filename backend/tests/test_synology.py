from pathlib import Path

from app.services.synology_service import SynologyService


def test_lists_configured_directory_volume(tmp_path: Path) -> None:
    volume = SynologyService({"media": str(tmp_path)}).list_volumes()[0]

    assert volume.name == "media"
    assert volume.path == str(tmp_path.resolve())
    assert 0 <= volume.usage_percent <= 100
