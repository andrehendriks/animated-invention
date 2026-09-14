import httpx

from app.models import PullRequestSummary


class GitHubService:
    """Read configured repository metadata through GitHub's REST API."""

    def __init__(
        self, repositories: list[str], token: str = "", transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self._repositories = repositories
        self._token = token
        self._transport = transport

    async def list_open_pull_requests(self) -> list[PullRequestSummary]:
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        pull_requests: list[PullRequestSummary] = []
        async with httpx.AsyncClient(timeout=15, transport=self._transport) as client:
            for repository in self._repositories:
                response = await client.get(
                    f"https://api.github.com/repos/{repository}/pulls",
                    params={"state": "open", "per_page": 30},
                    headers=headers,
                )
                response.raise_for_status()
                for pull_request in response.json():
                    pull_requests.append(
                        PullRequestSummary(
                            repository=repository,
                            number=pull_request["number"],
                            title=pull_request["title"],
                            author=pull_request["user"]["login"],
                            url=pull_request["html_url"],
                            draft=pull_request.get("draft", False),
                        )
                    )
        return pull_requests
