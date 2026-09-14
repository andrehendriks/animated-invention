import asyncio
import json

import httpx

from app.services.github_service import GitHubService


def test_lists_open_pull_requests_for_configured_repositories() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            content=json.dumps([{
                "number": 42,
                "title": "Improve monitoring",
                "user": {"login": "atlas-user"},
                "html_url": "https://github.com/example/atlas/pull/42",
                "draft": False,
            }]),
        )
    )

    pull_requests = asyncio.run(
        GitHubService(["example/atlas"], transport=transport).list_open_pull_requests()
    )

    assert pull_requests[0].repository == "example/atlas"
    assert pull_requests[0].number == 42
