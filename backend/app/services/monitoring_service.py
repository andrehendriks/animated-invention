import httpx

from app.models import MonitoringAlert, MonitoringTarget


class MonitoringService:
    """Read alert and scrape-target state from a Prometheus-compatible API."""

    def __init__(self, base_url: str, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._transport = transport

    async def _get_data(self, path: str) -> dict:
        async with httpx.AsyncClient(timeout=15, transport=self._transport) as client:
            response = await client.get(f"{self._base_url}{path}")
            response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "success" or not isinstance(payload.get("data"), dict):
            raise ValueError("Prometheus returned an invalid response")
        return payload["data"]

    async def list_alerts(self) -> list[MonitoringAlert]:
        data = await self._get_data("/api/v1/alerts")
        return [
            MonitoringAlert(
                name=alert.get("labels", {}).get("alertname", "Unnamed alert"),
                state=alert.get("state", "unknown"),
                severity=alert.get("labels", {}).get("severity", "unknown"),
                summary=alert.get("annotations", {}).get("summary", ""),
                active_at=alert.get("activeAt"),
            )
            for alert in data.get("alerts", [])
        ]

    async def list_targets(self) -> list[MonitoringTarget]:
        data = await self._get_data("/api/v1/targets")
        return [
            MonitoringTarget(
                job=target.get("labels", {}).get("job", "unknown"),
                instance=target.get("labels", {}).get("instance", "unknown"),
                health=target.get("health", "unknown"),
                last_error=target.get("lastError", ""),
            )
            for target in data.get("activeTargets", [])
        ]
