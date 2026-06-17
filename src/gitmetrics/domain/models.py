from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class Author(BaseModel):
    model_config = ConfigDict(frozen=True)

    login: str
    name: str | None = None


class Commit(BaseModel):
    model_config = ConfigDict(frozen=True)

    sha: str
    message: str
    author: Author
    date: datetime


class CommitMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)

    total: int
    conventional: int
    by_type: dict[str, int]


class AuthorStats(BaseModel):
    model_config = ConfigDict(frozen=True)

    author: Author
    commit_count: int
    conventional_rate: float


class AuditReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    repo: str
    period: tuple[date, date]
    commits: list[Commit]
    author_stats: list[AuthorStats]
    summary: CommitMetrics
