import re
from collections import defaultdict

from gitmetrics.domain.models import Author, AuthorStats, Commit, CommitMetrics

CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|chore|build|ci)(\(.+\))?!?: .+"
)


def is_conventional(message: str) -> bool:
    subject = _subject_line(message)
    return CONVENTIONAL_COMMIT_RE.match(subject) is not None


def parse_commit_type(message: str) -> str | None:
    subject = _subject_line(message)
    match = CONVENTIONAL_COMMIT_RE.match(subject)
    if not match:
        return None
    return match.group(1)


def conventional_percentage(metrics: CommitMetrics) -> float:
    if metrics.total == 0:
        return 0.0
    return round(metrics.conventional / metrics.total * 100, 2)


class CommitAnalyzer:
    def analyze(self, commits: list[Commit]) -> tuple[CommitMetrics, list[AuthorStats]]:
        by_type: dict[str, int] = defaultdict(int)
        conventional = 0

        author_totals: dict[str, int] = defaultdict(int)
        author_conventional: dict[str, int] = defaultdict(int)
        authors: dict[str, Author] = {}

        for commit in commits:
            login = commit.author.login
            authors[login] = commit.author
            author_totals[login] += 1

            if is_conventional(commit.message):
                conventional += 1
                author_conventional[login] += 1
                commit_type = parse_commit_type(commit.message)
                if commit_type:
                    by_type[commit_type] += 1

        summary = CommitMetrics(
            total=len(commits),
            conventional=conventional,
            by_type=dict(by_type),
        )

        author_stats = [
            AuthorStats(
                author=authors[login],
                commit_count=author_totals[login],
                conventional_rate=_author_conventional_rate(
                    author_totals[login],
                    author_conventional[login],
                ),
            )
            for login in sorted(authors)
        ]

        return summary, author_stats


def _subject_line(message: str) -> str:
    return message.splitlines()[0].strip()


def _author_conventional_rate(total: int, conventional: int) -> float:
    if total == 0:
        return 0.0
    return round(conventional / total, 4)
