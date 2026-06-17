import typer

app = typer.Typer(
    name="gitmetrics",
    help="GitMetrics — аудит активности репозитория на GitHub",
    no_args_is_help=True,
)


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
    from gitmetrics.infrastructure.config import load_settings

    settings = load_settings()
    typer.echo(
        f"Аудит {owner}/{repo} с {since} по {until} "
        f"(format={output_format}, log_level={settings.log_level}) — not implemented"
    )
