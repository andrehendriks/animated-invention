import asyncio
import json

import httpx

from app.services.monitoring_service import MonitoringService


def test_lists_prometheus_alerts() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            content=json.dumps(
                {"status": "success", "data": {"alerts": [{
                    "labels": {"alertname": "DiskFull", "severity": "critical"},
                    "annotations": {"summary": "The backup volume is full"},
                    "state": "firing",
                }]}}
            ),
        )
    )

    alerts = asyncio.run(MonitoringService("http://prometheus", transport).list_alerts())

    assert alerts[0].name == "DiskFull"
    assert alerts[0].state == "firing"
