# GitMetrics

Консольная утилита для аудита активности Git-репозитория на GitHub: загрузка коммитов за период, проверка Conventional Commits, метрики по авторам, отчёты JSON/Markdown.

**Команда:** Володин · Ракшин · Бадмаев

---

## Требования

- Python 3.12+
- GitHub Personal Access Token ([создать токен](https://github.com/settings/tokens))
- Docker (опционально, для контейнерного запуска)

---

## Установка

```bash
git clone https://github.com/<owner>/GitMetrics.git
cd GitMetrics
pip install -e ".[dev]"
```

---

## Настройка `.env`

Скопируйте шаблон и укажите свой токен:

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # Linux / macOS
```

Содержимое `.env`:

```env
GITHUB_TOKEN=ghp_your_token_here
LOG_LEVEL=INFO
LOG_DIR=logs
```

> Файл `.env` не коммитится в репозиторий. В git хранится только `.env.example`.

---

## Локальный запуск

Справка:

```bash
gitmetrics --help
gitmetrics audit --help
```

Пример аудита репозитория:

```bash
gitmetrics audit \
  --owner octocat \
  --repo Hello-World \
  --since 2025-01-01 \
  --until 2025-06-01 \
  --format json,md \
  --output ./reports
```

Windows (PowerShell):

```powershell
gitmetrics audit --owner octocat --repo Hello-World --since 2025-01-01 --until 2025-06-01
```

---

## Docker

### Сборка образа

```bash
docker build -t gitmetrics .
```

### Запуск

```bash
docker run --rm --env-file .env gitmetrics --help

docker run --rm --env-file .env gitmetrics audit \
  --owner octocat \
  --repo Hello-World \
  --since 2025-01-01 \
  --until 2025-06-01 \
  --format json,md
```

Сохранить отчёты на хост (монтирование директории):

```bash
docker run --rm --env-file .env -v "%cd%/reports:/app/reports" gitmetrics audit \
  --owner octocat \
  --repo Hello-World \
  --since 2025-01-01 \
  --until 2025-06-01 \
  --output /app/reports
```

Логи дублируются в консоль и в `{LOG_DIR}/gitmetrics.log` (по умолчанию `logs/`). Для сохранения логов с хоста:

```bash
docker run --rm --env-file .env -v "%cd%/logs:/app/logs" gitmetrics audit \
  --owner octocat \
  --repo Hello-World \
  --since 2025-01-01 \
  --until 2025-06-01
```

---

## Разработка

```bash
ruff check src tests
pytest --cov=gitmetrics
```

---

## Структура проекта

```
src/gitmetrics/
  presentation/    # CLI (Typer)
  application/     # Use cases
  domain/          # Модели и бизнес-правила
  infrastructure/  # GitHub API, writers, config
```
