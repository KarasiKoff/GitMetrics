from datetime import date
from typing import Protocol

from gitmetrics.domain.models import AuditReport, Commit


class CommitRepository(Protocol):
    def fetch_commits(
        self,
        owner: str,
        repo: str,
        since: date,
        until: date,
    ) -> list[Commit]: ...


class ReportWriter(Protocol):
    def write(self, report: AuditReport, path: str) -> None: ...
