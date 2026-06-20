from pathlib import Path

from gitmetrics.domain.models import AuditReport


class JsonReportWriter:
    def write(self, report: AuditReport, path: str) -> None:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
