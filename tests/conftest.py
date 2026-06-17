import json
from collections.abc import Iterator
from pathlib import Path

import pytest
import respx
from httpx import Response

FIXTURES_DIR = Path(__file__).parent / "fixtures"
GITHUB_COMMITS_URL = (
    r"https://api\.github\.com/repos/[\w.-]+/[\w.-]+/commits(\?.*)?$"
)


@pytest.fixture
def sample_commits() -> list[dict]:
    """GitHub REST API payload: список коммитов из fixtures."""
    path = FIXTURES_DIR / "sample_commits.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def mock_github_response(sample_commits: list[dict]) -> Iterator[respx.MockRouter]:
    """respx-мок эндпоинта GET /repos/{owner}/{repo}/commits."""
    with respx.mock(assert_all_called=False) as router:
        router.get(url__regex=GITHUB_COMMITS_URL).respond(
            Response(200, json=sample_commits)
        )
        yield router
