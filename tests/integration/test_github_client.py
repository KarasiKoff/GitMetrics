from datetime import date

import pytest
import respx

from gitmetrics.infrastructure.github_client import (
    GitHubAuthError,
    GitHubClient,
    GitHubNotFoundError,
)

GITHUB_COMMITS_URL = (
    r"https://api\.github\.com/repos/[\w.-]+/[\w.-]+/commits(\?.*)?$"
)


def _github_commit(sha: str, message: str, login: str) -> dict:
    return {
        "sha": sha,
        "commit": {
            "message": message,
            "author": {
                "name": login,
                "email": f"{login}@example.com",
                "date": "2025-03-10T09:15:00Z",
            },
        },
        "author": {"login": login, "id": 1},
    }


def test_fetch_commits_returns_parsed_commits(
    mock_github_response: respx.MockRouter,
    sample_commits: list[dict],
) -> None:
    with GitHubClient("test-token") as client:
        commits = client.fetch_commits(
            "octocat",
            "Hello-World",
            date(2025, 1, 1),
            date(2025, 6, 1),
        )

    assert len(commits) == len(sample_commits)
    assert commits[0].sha == sample_commits[0]["sha"]
    assert commits[0].message == "feat: add commit analyzer"
    assert commits[0].author.login == "alice"


def test_fetch_commits_raises_auth_error_on_401() -> None:
    with respx.mock:
        respx.get(url__regex=GITHUB_COMMITS_URL).respond(
            401, json={"message": "Bad credentials"}
        )

        with GitHubClient("bad-token") as client:
            with pytest.raises(GitHubAuthError):
                client.fetch_commits(
                    "octocat",
                    "Hello-World",
                    date(2025, 1, 1),
                    date(2025, 6, 1),
                )


def test_fetch_commits_raises_not_found_on_404() -> None:
    with respx.mock:
        respx.get(url__regex=GITHUB_COMMITS_URL).respond(
            404, json={"message": "Not Found"}
        )

        with GitHubClient("test-token") as client:
            with pytest.raises(GitHubNotFoundError):
                client.fetch_commits(
                    "octocat",
                    "missing-repo",
                    date(2025, 1, 1),
                    date(2025, 6, 1),
                )


def test_fetch_commits_follows_pagination() -> None:
    page1 = [_github_commit("a" * 40, "feat: page one", "alice")]
    page2 = [_github_commit("b" * 40, "fix: page two", "bob")]
    next_link = (
        '<https://api.github.com/repos/octocat/Hello-World/commits'
        '?page=2&per_page=100>; rel="next"'
    )

    with respx.mock:
        respx.get(
            "/repos/octocat/Hello-World/commits",
            params={
                "since": "2025-01-01T00:00:00Z",
                "until": "2025-06-01T23:59:59Z",
                "per_page": "100",
            },
        ).respond(200, json=page1, headers={"Link": next_link})
        respx.get(
            "/repos/octocat/Hello-World/commits",
            params={"page": "2", "per_page": "100"},
        ).respond(200, json=page2)

        with GitHubClient("test-token") as client:
            commits = client.fetch_commits(
                "octocat",
                "Hello-World",
                date(2025, 1, 1),
                date(2025, 6, 1),
            )

    assert len(commits) == 2
    assert commits[0].message == "feat: page one"
    assert commits[1].message == "fix: page two"
    assert commits[0].author.login == "alice"
    assert commits[1].author.login == "bob"
