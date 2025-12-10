# syntax=docker/dockerfile:1

# 1) Сборка зависимостей с uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder
WORKDIR /app

# Кэшируем установку зависимостей по lock-файлам
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Добавляем исходники и синхронизируем проект (если он инсталируется как пакет)
COPY . .
RUN uv sync --frozen --no-dev

# 2) Рантайм-образ
FROM python:3.12-slim AS runner
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
WORKDIR /app

# Копируем готовое окружение
COPY --from=builder /app/.venv ${VIRTUAL_ENV}

# Копируем только то, что нужно для рантайма
COPY app ./app
COPY config ./config
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY main.py .
COPY pyproject.toml uv.lock ./

# Dynaconf: читаем settings + secrets (секреты будут смонтированы в compose)
ENV DYNACONF_SETTINGS="/app/config/settings.toml,/app/config/.secrets.toml" \
    DYNACONF_ENV=development

CMD ["python", "main.py"]