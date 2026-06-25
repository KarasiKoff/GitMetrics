# Тестирование GitMetrics

## Требования

- Python 3.12+
- Dev-зависимости: `pip install -e ".[dev]"`

## Запуск тестов

```bash
python -m pytest
```

С отчётом покрытия:

```bash
python -m pytest --cov=gitmetrics --cov-report=term-missing
```

## Структура тестов

| Каталог | Назначение |
|---------|------------|
| `tests/unit/` | Unit-тесты анализатора и writers |
| `tests/integration/` | Интеграционные тесты GitHub-клиента (respx) |
| `tests/conftest.py` | Фикстуры `sample_commits`, `mock_github_response` |
| `tests/fixtures/` | JSON-фикстуры для моков GitHub API |

## Линтер

```bash
python -m ruff check .
```

## Отчёты для КТ №3

| Файл | Команда |
|------|---------|
| `docs/linter-report.txt` | `ruff check .` |
| `docs/coverage-report.txt` | `pytest --cov=gitmetrics --cov-report=term-missing` |

Перегенерировать отчёты:

```bash
python -m ruff check . > docs/linter-report.txt
python -m pytest --cov=gitmetrics --cov-report=term-missing > docs/coverage-report.txt
```

На Windows (PowerShell):

```powershell
python -m ruff check . 2>&1 | Out-File docs/linter-report.txt -Encoding utf8
python -m pytest --cov=gitmetrics --cov-report=term-missing 2>&1 | Out-File docs/coverage-report.txt -Encoding utf8
```

## Интерпретация coverage

- **73%+** — текущее покрытие ядра (domain, infrastructure writers, github client)
- **0%** у `cli.py`, `config.py`, `audit_use_case.py` — не покрыты unit-тестами (проверяются отдельно e2e-сценариями)

## Exit codes pytest

| Код | Значение |
|-----|----------|
| 0 | Все тесты прошли |
| 1 | Есть упавшие тесты |
| 5 | Тесты не найдены |
