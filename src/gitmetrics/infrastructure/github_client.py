import re
from datetime import date, datetime, time, timezone
from typing import Any
from urllib.parse import urlparse

import httpx

from gitmetrics.domain.models import Author, Commit

GITHUB_API_BASE = "https://api.github.com"


class GitHubError(Exception):
    """Базовая ошибка GitHub API."""


class GitHubAuthError(GitHubError):
    """401 — неверный или отсутствующий токен."""


class GitHubNotFoundError(GitHubError):
    """404 — репозиторий не найден."""


class GitHubRateLimitError(GitHubError):
    """403 — превышен лимит запросов к API."""


class GitHubClient:
    def __init__(self, token: str, *, client: httpx.Client | None = None) -> None:
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=GITHUB_API_BASE,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "GitHubClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def fetch_commits(
        self,
        owner: str,
        repo: str,
        since: date,
        until: date,
    ) -> list[Commit]:
        commits: list[Commit] = []
        url: str | None = f"/repos/{owner}/{repo}/commits"
        params: dict[str, str | int] | None = {
            "since": _date_to_iso(since, end_of_day=False),
            "until": _date_to_iso(until, end_of_day=True),
            "per_page": 100,
        }

        while url:
            response = self._client.get(url, params=params)
            params = None
            _raise_for_status(response)

            for item in response.json():
                commits.append(_parse_commit(item))

            url = _parse_next_link(response.headers.get("Link"))

        return commits


def _date_to_iso(value: date, *, end_of_day: bool) -> str:
    if end_of_day:
        dt = datetime.combine(value, time(23, 59, 59), tzinfo=timezone.utc)
    else:
        dt = datetime.combine(value, time.min, tzinfo=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def _parse_next_link(link_header: str | None) -> str | None:
    if not link_header:
        return None

    for part in link_header.split(","):
        section = part.strip()
        if 'rel="next"' not in section:
            continue
        match = re.search(r"<([^>]+)>", section)
        if not match:
            continue
        parsed = urlparse(match.group(1))
        if parsed.query:
            return f"{parsed.path}?{parsed.query}"
        return parsed.path

    return None


def _parse_commit(data: dict[str, Any]) -> Commit:
    commit_data = data["commit"]
    git_author = commit_data["author"]
    gh_author = data.get("author")

    if gh_author and gh_author.get("login"):
        login = gh_author["login"]
        name = gh_author.get("name") or git_author.get("name")
    else:
        login = git_author.get("email") or "[unknown]"
        name = git_author.get("name")

    date_str = git_author["date"].replace("Z", "+00:00")

    return Commit(
        sha=data["sha"],
        message=commit_data["message"],
        author=Author(login=login, name=name),
        date=datetime.fromisoformat(date_str),
    )


def _is_rate_limited(response: httpx.Response) -> bool:
    remaining = response.headers.get("X-RateLimit-Remaining")
    if remaining == "0":
        return True

    try:
        message = response.json().get("message", "").lower()
    except ValueError:
        return False

    return "rate limit" in message


def _raise_for_status(response: httpx.Response) -> None:
    if response.status_code == 401:
        raise GitHubAuthError("GitHub API: неверный или отсутствующий токен (401)")

    if response.status_code == 404:
        raise GitHubNotFoundError("GitHub API: репозиторий не найден (404)")

    if response.status_code == 403 and _is_rate_limited(response):
        raise GitHubRateLimitError("GitHub API: превышен лимит запросов (403)")

    response.raise_for_status()
