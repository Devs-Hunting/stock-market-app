FROM python:3.11-slim
LABEL maintainer="rafal-gbc"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock /app/
COPY ./src/deployment/mikrus/scripts/ /scripts
COPY ./src/psmproject /app/
COPY ./README.md /app/

RUN poetry config virtualenvs.create false \
    && poetry install && \
    sed -i 's/\r$//' /scripts/run.sh && \
    chmod -R +x /scripts

ENV PATH="/scripts::$PATH"

CMD ["run.sh"]
