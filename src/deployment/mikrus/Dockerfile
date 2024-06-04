FROM python:3.11-alpine AS builder
LABEL maintainer="rafal-gbc"

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

COPY ./pyproject.toml ./poetry.lock /app/
COPY ./src/psmproject /app/
COPY ./README.md /app/

WORKDIR /app

RUN pip install poetry

RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-root \
    && rm -rf $POETRY_CACHE_DIR \
    && pip uninstall poetry -y


FROM python:3.11-alpine AS runner
WORKDIR /app

RUN apk add --no-cache curl gettext

COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app /app
COPY ./src/deployment/mikrus/scripts /scripts

ENV PATH="/usr/local/bin:/scripts:$PATH"
RUN sed -i 's/\r$//' /scripts/app/run.sh \
    && sed -i 's/\r$//' /scripts/app/reset_db_data.sh \
    && sed -i 's/\r$//' /scripts/worker/run.sh \
    && chmod -R +x /scripts \
    && mkdir static/ \
    && chown -R nobody:nogroup /app/project_static/ /app/static/ /app/media/ /app/*/migrations/

USER nobody
