FROM python:3.11-slim
LABEL maintainer="rafal-gbc"

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt-get update \
    && apt-get -y install curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock /app/
COPY ./src/psmproject /app/
COPY ./README.md /app/

COPY ./src/deployment/mikrus/scripts/app/run.sh /start-app
RUN sed -i 's/\r$//g' /start-app && \
    chmod +x /start-app

COPY ./src/deployment/mikrus/scripts/websocket/run.sh /start-websocket
RUN sed -i 's/\r$//g' /start-websocket && \
    chmod +x /start-websocket

COPY ./src/deployment/mikrus/scripts/worker/run.sh /start-worker
RUN sed -i 's/\r$//g' /start-worker && \
    chmod +x /start-worker

WORKDIR /app

RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-root \
    && rm -rf $POETRY_CACHE_DIR
