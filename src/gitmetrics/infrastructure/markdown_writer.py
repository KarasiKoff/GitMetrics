from pathlib import Path

from gitmetrics.domain.commit_analyzer import conventional_percentage, is_conventional
from gitmetrics.domain.models import AuditReport

TOP_VIOLATIONS_LIMIT = 10


class MarkdownReportWriter:
    def write(self, report: AuditReport, path: str) -> None:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(_render(report), encoding="utf-8")


def _render(report: AuditReport) -> str:
    since, until = report.period
    pct = conventional_percentage(report.summary)
    lines = [
        "# GitMetrics Audit Report",
        "",
        f"**Repository:** {report.repo}",
        f"**Period:** {since.isoformat()} — {until.isoformat()}",
        "",
        "## Summary",
        "",
        f"- Total commits: {report.summary.total}",
        f"- Conventional: {report.summary.conventional} ({pct}%)",
        f"- Non-conventional: {report.summary.total - report.summary.conventional}",
        "",
    ]

    if report.summary.by_type:
        lines.extend(["### By type", ""])
        for commit_type, count in sorted(report.summary.by_type.items()):
            lines.append(f"- `{commit_type}`: {count}")
        lines.append("")

    lines.extend(["## Authors", "", _authors_table(report), ""])
    lines.extend(["## Top violations", "", _violations_section(report)])

    return "\n".join(lines)


def _authors_table(report: AuditReport) -> str:
    header = "| Author | Commits | Conventional rate |"
    separator = "| --- | ---: | ---: |"
    rows = [
        (
            f"| {stat.author.login} | {stat.commit_count} | "
            f"{stat.conventional_rate * 100:.1f}% |"
        )
        for stat in report.author_stats
    ]
    return "\n".join([header, separator, *rows])


def _violations_section(report: AuditReport) -> str:
    violations = [
        commit
        for commit in report.commits
        if not is_conventional(commit.message)
    ]
    violations.sort(key=lambda commit: commit.date, reverse=True)
    violations = violations[:TOP_VIOLATIONS_LIMIT]

    if not violations:
        return "No non-conventional commits found."

    header = "| SHA | Author | Message |"
    separator = "| --- | --- | --- |"
    rows = [
        (
            f"| `{commit.sha[:7]}` | {commit.author.login} | "
            f"{_escape_cell(_subject(commit.message))} |"
        )
        for commit in violations
    ]
    return "\n".join([header, separator, *rows])


def _subject(message: str) -> str:
    return message.splitlines()[0].strip()


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|")
