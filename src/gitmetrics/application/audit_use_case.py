from datetime import date
from pathlib import Path

from gitmetrics.domain.commit_analyzer import CommitAnalyzer
from gitmetrics.domain.interfaces import CommitRepository
from gitmetrics.domain.models import AuditReport
from gitmetrics.infrastructure.json_writer import JsonReportWriter
from gitmetrics.infrastructure.markdown_writer import MarkdownReportWriter


class AuditUseCase:
    def __init__(
        self,
        commit_repository: CommitRepository,
        analyzer: CommitAnalyzer | None = None,
        json_writer: JsonReportWriter | None = None,
        markdown_writer: MarkdownReportWriter | None = None,
    ) -> None:
        self._commit_repository = commit_repository
        self._analyzer = analyzer or CommitAnalyzer()
        self._json_writer = json_writer or JsonReportWriter()
        self._markdown_writer = markdown_writer or MarkdownReportWriter()

    def execute(
        self,
        owner: str,
        repo: str,
        since: date,
        until: date,
        formats: list[str],
        output_dir: str,
    ) -> AuditReport:
        commits = self._commit_repository.fetch_commits(owner, repo, since, until)
        summary, author_stats = self._analyzer.analyze(commits)

        report = AuditReport(
            repo=f"{owner}/{repo}",
            period=(since, until),
            commits=commits,
            author_stats=author_stats,
            summary=summary,
        )

        output = Path(output_dir)
        normalized_formats = {item.strip().lower() for item in formats}

        if "json" in normalized_formats:
            self._json_writer.write(report, str(output / "report.json"))

        if "md" in normalized_formats or "markdown" in normalized_formats:
            self._markdown_writer.write(report, str(output / "report.md"))

        return report
