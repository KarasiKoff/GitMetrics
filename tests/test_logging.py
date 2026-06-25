import logging
from datetime import date

import pytest
import respx

from gitmetrics.infrastructure.github_client import (
    GitHubClient,
    GitHubNotFoundError,
    GitHubRateLimitError,
)
from gitmetrics.infrastructure.logging import LOG_FILENAME, LOG_FORMAT, setup_logging


@pytest.fixture(autouse=True)
def _reset_logging() -> None:
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    root.setLevel(logging.WARNING)


def test_setup_logging_sets_level_and_format(tmp_path) -> None:
    setup_logging("DEBUG", log_dir=str(tmp_path))

    root = logging.getLogger()
    assert root.level == logging.DEBUG
    assert len(root.handlers) == 2

    formatters = {handler.formatter._fmt for handler in root.handlers}
    assert formatters == {LOG_FORMAT}


def test_setup_logging_invalid_level_defaults_to_info(tmp_path) -> None:
    setup_logging("NOT_A_LEVEL", log_dir=str(tmp_path))
    assert logging.getLogger().level == logging.INFO


def test_setup_logging_writes_to_file(tmp_path) -> None:
    setup_logging("INFO", log_dir=str(tmp_path))
    logging.getLogger("gitmetrics.test").info("hello file")

    for handler in logging.getLogger().handlers:
        handler.flush()
        handler.close()

    log_file = tmp_path / LOG_FILENAME
    assert log_file.exists()
    assert "hello file" in log_file.read_text(encoding="utf-8")


def test_github_client_logs_commit_count(
    mock_github_response: respx.MockRouter,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(
        logging.INFO, logger="gitmetrics.infrastructure.github_client"
    ):
        with GitHubClient("test-token") as client:
            commits = client.fetch_commits(
                "octocat",
                "Hello-World",
                date(2025, 1, 1),
                date(2025, 6, 1),
            )

    assert len(commits) == 5
    assert "Получено 5 коммитов для octocat/Hello-World" in caplog.text


def test_github_client_logs_empty_result_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with respx.mock:
        respx.get(url__regex=r"https://api\.github\.com/repos/.+/commits.*").respond(
            200, json=[]
        )

        with caplog.at_level(
            logging.WARNING, logger="gitmetrics.infrastructure.github_client"
        ):
            with GitHubClient("test-token") as client:
                commits = client.fetch_commits(
                    "octocat",
                    "Hello-World",
                    date(2025, 1, 1),
                    date(2025, 6, 1),
                )

    assert commits == []
    assert "Пустой результат" in caplog.text


def test_github_client_logs_rate_limit_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with respx.mock:
        respx.get(url__regex=r"https://api\.github\.com/repos/.+/commits.*").respond(
            403,
            json={"message": "API rate limit exceeded"},
            headers={"X-RateLimit-Remaining": "0"},
        )

        with caplog.at_level(
            logging.WARNING, logger="gitmetrics.infrastructure.github_client"
        ):
            with GitHubClient("test-token") as client:
                with pytest.raises(GitHubRateLimitError):
                    client.fetch_commits(
                        "octocat",
                        "Hello-World",
                        date(2025, 1, 1),
                        date(2025, 6, 1),
                    )

    assert "превышен лимит запросов" in caplog.text


def test_github_client_logs_api_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with respx.mock:
        respx.get(url__regex=r"https://api\.github\.com/repos/.+/commits.*").respond(
            404, json={"message": "Not Found"}
        )

        with caplog.at_level(
            logging.ERROR, logger="gitmetrics.infrastructure.github_client"
        ):
            with GitHubClient("test-token") as client:
                with pytest.raises(GitHubNotFoundError):
                    client.fetch_commits(
                        "octocat",
                        "missing-repo",
                        date(2025, 1, 1),
                        date(2025, 6, 1),
                    )

    assert "репозиторий не найден" in caplog.text
