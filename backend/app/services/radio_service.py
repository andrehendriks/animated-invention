import httpx

from app.models import RadioMount, RadioStatus


class RadioService:
    """Collect public status data from configured Icecast and Liquidsoap endpoints."""

    def __init__(
        self,
        icecast_status_url: str,
        liquidsoap_health_url: str = "",
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._icecast_status_url = icecast_status_url
        self._liquidsoap_health_url = liquidsoap_health_url
        self._transport = transport

    async def get_status(self) -> RadioStatus:
        async with httpx.AsyncClient(timeout=15, transport=self._transport) as client:
            icecast_response = await client.get(self._icecast_status_url)
            icecast_response.raise_for_status()
            liquidsoap_healthy = None
            if self._liquidsoap_health_url:
                liquidsoap_response = await client.get(self._liquidsoap_health_url)
                liquidsoap_healthy = liquidsoap_response.is_success

        source = icecast_response.json().get("icestats", {}).get("source", [])
        sources = source if isinstance(source, list) else [source]
        return RadioStatus(
            icecast_healthy=True,
            liquidsoap_healthy=liquidsoap_healthy,
            mounts=[
                RadioMount(
                    name=item.get("listenurl", item.get("server_name", "unknown")),
                    listeners=int(item.get("listeners", 0)),
                    bitrate_kbps=int(item["bitrate"]) if str(item.get("bitrate", "")).isdigit() else None,
                    title=item.get("title", ""),
                    listen_url=item.get("listenurl", ""),
                )
                for item in sources
                if isinstance(item, dict)
            ],
        )
