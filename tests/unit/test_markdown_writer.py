from datetime import date, datetime

from gitmetrics.domain.models import (
    AuditReport,
    Author,
    AuthorStats,
    Commit,
    CommitMetrics,
)
from gitmetrics.infrastructure.markdown_writer import MarkdownReportWriter


def test_markdown_writer_creates_report_with_summary_and_violations(tmp_path) -> None:
    report = AuditReport(
        repo="octocat/Hello-World",
        period=(date(2025, 1, 1), date(2025, 1, 31)),
        commits=[
            Commit(
                sha="a" * 40,
                message="feat: add login",
                author=Author(login="alice"),
                date=datetime(2025, 1, 10, 12, 0, 0),
            ),
            Commit(
                sha="b" * 40,
                message="bad commit message",
                author=Author(login="bob"),
                date=datetime(2025, 1, 11, 12, 0, 0),
            ),
        ],
        author_stats=[
            AuthorStats(
                author=Author(login="alice"),
                commit_count=1,
                conventional_rate=1.0,
            ),
            AuthorStats(
                author=Author(login="bob"),
                commit_count=1,
                conventional_rate=0.0,
            ),
        ],
        summary=CommitMetrics(total=2, conventional=1, by_type={"feat": 1}),
    )

    output = tmp_path / "report.md"
    MarkdownReportWriter().write(report, str(output))
    content = output.read_text(encoding="utf-8")

    assert output.exists()
    assert "# GitMetrics Audit Report" in content
    assert "**Repository:** octocat/Hello-World" in content
    assert "Total commits: 2" in content
    assert "Conventional: 1 (50.0%)" in content
    assert "| alice | 1 | 100.0% |" in content
    assert "bad commit message" in content
