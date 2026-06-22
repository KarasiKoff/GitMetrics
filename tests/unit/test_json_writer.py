import json
from datetime import date, datetime

from gitmetrics.domain.models import (
    AuditReport,
    Author,
    AuthorStats,
    Commit,
    CommitMetrics,
)
from gitmetrics.infrastructure.json_writer import JsonReportWriter


def test_json_writer_creates_valid_report_file(tmp_path) -> None:
    report = AuditReport(
        repo="octocat/Hello-World",
        period=(date(2025, 1, 1), date(2025, 1, 31)),
        commits=[
            Commit(
                sha="a" * 40,
                message="feat: add login",
                author=Author(login="alice", name="Alice"),
                date=datetime(2025, 1, 10, 12, 0, 0),
            )
        ],
        author_stats=[
            AuthorStats(
                author=Author(login="alice", name="Alice"),
                commit_count=1,
                conventional_rate=1.0,
            )
        ],
        summary=CommitMetrics(total=1, conventional=1, by_type={"feat": 1}),
    )

    output = tmp_path / "report.json"
    JsonReportWriter().write(report, str(output))

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert output.exists()
    assert payload["repo"] == "octocat/Hello-World"
    assert payload["period"] == ["2025-01-01", "2025-01-31"]
    assert payload["summary"]["total"] == 1
    assert payload["summary"]["conventional"] == 1
    assert payload["commits"][0]["message"] == "feat: add login"
