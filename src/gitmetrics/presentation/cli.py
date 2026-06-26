import logging
from datetime import date

import typer

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="gitmetrics",
    help="GitMetrics — аудит активности репозитория на GitHub",
    no_args_is_help=True,
)


def _parse_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        msg = f"{field_name} должен быть в формате YYYY-MM-DD, получено: {value!r}"
        raise typer.BadParameter(msg) from exc


def _parse_formats(value: str) -> list[str]:
    formats = [item.strip() for item in value.split(",") if item.strip()]
    if not formats:
        raise typer.BadParameter("Укажите хотя бы один формат: json, md")
    return formats


@app.command()
def version() -> None:
    """Показать версию утилиты."""
    from gitmetrics import __version__

    typer.echo(__version__)


@app.command()
def audit(
    owner: str = typer.Option(..., help="Владелец репозитория (GitHub owner)"),
    repo: str = typer.Option(..., help="Название репозитория"),
    since: str = typer.Option(..., help="Начало периода (YYYY-MM-DD)"),
    until: str = typer.Option(..., help="Конец периода (YYYY-MM-DD)"),
    output_format: str = typer.Option(
        "json,md",
        "--format",
        help="Форматы отчёта через запятую: json, md",
    ),
    output_dir: str = typer.Option(".", "--output", help="Директория для отчётов"),
) -> None:
    """Запустить аудит репозитория за указанный период."""
    from gitmetrics.application.audit_use_case import AuditUseCase
    from gitmetrics.domain.commit_analyzer import conventional_percentage
    from gitmetrics.infrastructure.config import load_settings
    from gitmetrics.infrastructure.github_client import (
        GitHubAuthError,
        GitHubClient,
        GitHubError,
        GitHubNotFoundError,
        GitHubRateLimitError,
    )
    from gitmetrics.infrastructure.logging import setup_logging

    settings = load_settings()
    setup_logging(settings.log_level, settings.log_dir)

    since_date = _parse_date(since, "since")
    until_date = _parse_date(until, "until")
    if since_date > until_date:
        raise typer.BadParameter("since не может быть позже until")

    formats = _parse_formats(output_format)
    repo_ref = f"{owner}/{repo}"
    logger.info("Аудит начат: %s, период %s — %s", repo_ref, since, until)

    try:
        with GitHubClient(token=settings.github_token) as client:
            use_case = AuditUseCase(commit_repository=client)
            report = use_case.execute(
                owner=owner,
                repo=repo,
                since=since_date,
                until=until_date,
                formats=formats,
                output_dir=output_dir,
            )
    except GitHubAuthError:
        typer.secho(
            "Ошибка: неверный GitHub-токен. Проверьте GITHUB_TOKEN в .env",
            err=True,
        )
        raise typer.Exit(1) from None
    except GitHubNotFoundError:
        typer.secho(f"Ошибка: репозиторий {repo_ref} не найден", err=True)
        raise typer.Exit(1) from None
    except GitHubRateLimitError:
        typer.secho("Ошибка: превышен лимит запросов GitHub API", err=True)
        raise typer.Exit(1) from None
    except GitHubError as exc:
        logger.error("Ошибка GitHub API: %s", exc)
        typer.secho(f"Ошибка GitHub API: {exc}", err=True)
        raise typer.Exit(1) from None
    except OSError as exc:
        logger.error("Ошибка записи отчёта: %s", exc)
        typer.secho(f"Ошибка записи отчёта: {exc}", err=True)
        raise typer.Exit(1) from None

    pct = conventional_percentage(report.summary)
    typer.echo(
        f"Готово: {report.summary.total} коммитов, "
        f"{report.summary.conventional} conventional ({pct}%)"
    )
    if "json" in {f.lower() for f in formats}:
        typer.echo(f"JSON: {output_dir}/report.json")
    if "md" in {f.lower() for f in formats} or "markdown" in {
        f.lower() for f in formats
    }:
        typer.echo(f"Markdown: {output_dir}/report.md")

    logger.info("Аудит завершён: %d коммитов", report.summary.total)
