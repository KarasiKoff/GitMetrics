from datetime import UTC, datetime

import pytest

from gitmetrics.domain.commit_analyzer import (
    CommitAnalyzer,
    conventional_percentage,
    is_conventional,
    parse_commit_type,
)
from gitmetrics.domain.models import Author, Commit, CommitMetrics

CONVENTIONAL_CASES = [
    ("feat: add login", True),
    ("fix(api): handle 404", True),
    ("bad commit message", False),
    ("fix", False),
]


@pytest.mark.parametrize(("message", "expected"), CONVENTIONAL_CASES)
def test_is_conventional(message: str, expected: bool) -> None:
    assert is_conventional(message) is expected


def test_parse_commit_type_returns_type_for_conventional_message() -> None:
    assert parse_commit_type("feat: add login") == "feat"
    assert parse_commit_type("fix(api): handle 404") == "fix"


def test_parse_commit_type_returns_none_for_non_conventional_message() -> None:
    assert parse_commit_type("bad commit message") is None
    assert parse_commit_type("fix") is None


def test_conventional_percentage() -> None:
    metrics = CommitMetrics(total=4, conventional=3, by_type={"feat": 2, "fix": 1})
    assert conventional_percentage(metrics) == 75.0


def test_conventional_percentage_for_empty_metrics() -> None:
    metrics = CommitMetrics(total=0, conventional=0, by_type={})
    assert conventional_percentage(metrics) == 0.0


def test_analyze_aggregates_metrics_and_author_stats() -> None:
    commits = [
        Commit(
            sha="a" * 40,
            message="feat: add login",
            author=Author(login="alice"),
            date=datetime(2025, 1, 1, tzinfo=UTC),
        ),
        Commit(
            sha="b" * 40,
            message="fix(api): handle 404",
            author=Author(login="alice"),
            date=datetime(2025, 1, 2, tzinfo=UTC),
        ),
        Commit(
            sha="c" * 40,
            message="bad commit message",
            author=Author(login="bob"),
            date=datetime(2025, 1, 3, tzinfo=UTC),
        ),
    ]

    summary, author_stats = CommitAnalyzer().analyze(commits)

    assert summary.total == 3
    assert summary.conventional == 2
    assert summary.by_type == {"feat": 1, "fix": 1}
    assert len(author_stats) == 2
    assert author_stats[0].author.login == "alice"
    assert author_stats[0].commit_count == 2
    assert author_stats[0].conventional_rate == 1.0
    assert author_stats[1].author.login == "bob"
    assert author_stats[1].conventional_rate == 0.0
