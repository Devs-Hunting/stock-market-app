FROM python:3.10-alpine
LABEL maintainer="rafal-gbc"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY ./deployment/test/requirements.txt /tmp/requirements.txt
# COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./deployment/test/scripts /scripts

WORKDIR /psmproject

COPY ./psmproject /psmproject

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    # pip install -r /tmp/requirements.dev.txt && \
    rm -rf /tmp && \
    sed -i 's/\r$//' /scripts/run.sh && \
    chmod -R +x /scripts


ENV PATH="/scripts::$PATH"

CMD ["run.sh"]
