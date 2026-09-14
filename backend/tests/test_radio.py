import asyncio
import json

import httpx

from app.services.radio_service import RadioService


def test_reads_icecast_mount_status() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            content=json.dumps({"icestats": {"source": {
                "listenurl": "http://radio:8000/live",
                "listeners": 3,
                "bitrate": 128,
                "title": "Atlas FM",
            }}}),
        )
    )

    status = asyncio.run(RadioService("http://icecast/status-json.xsl", transport=transport).get_status())

    assert status.icecast_healthy
    assert status.mounts[0].listeners == 3
