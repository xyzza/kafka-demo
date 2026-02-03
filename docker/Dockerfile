# syntax=docker/dockerfile:1.14
ARG BASE_TARGET=python:3.14-slim

FROM $BASE_TARGET as base

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl git \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*


FROM base as builder

ARG INSTALL_DEV_DEPS

RUN --mount=type=tmpfs,target=/var/cache/apt \
    --mount=type=tmpfs,target=/var/lib/apt \
    --mount=type=tmpfs,target=/tmp \
    apt update && apt install -y --no-install-recommends \
    gcc \
    python3-dev  \
    ca-certificates  \
    curl \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

FROM base

ENTRYPOINT ["/app/docker/docker-entrypoint.sh"]

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY svc/ ./svc/