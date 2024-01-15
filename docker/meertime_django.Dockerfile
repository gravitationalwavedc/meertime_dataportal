# This Dockerfile builds the MeerTime Django application for deployment on Kubernetes.

FROM python:3.10-slim-buster

ARG DEVELOPMENT_MODE

ENV \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.3.2 \
  GET_POETRY_IGNORE_DEPRECATION=1 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  PATH="/root/.local/bin:$PATH"

# System dependencies:
RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    curl \
    gettext \
    git \
    wget \
    libpq-dev \
    python3-dev \
  # Installing `poetry` package manager:
  && curl -sSL https://install.python-poetry.org | python3 \
  && poetry --version \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

RUN adduser web

COPY --chown=web:web ./backend/pyproject.toml ./backend/poetry.lock /code/

# support development_mode in docker
RUN if [ "${DEVELOPMENT_MODE}" = "True" ]; then poetry install --with dev --no-interaction --no-ansi; else poetry install --no-interaction --no-ansi; fi;

COPY ./backend /code/

EXPOSE 8000

ENV GUNICORN_PARAMS="-b 0.0.0.0:8000 --workers 8 --timeout 600"
CMD [ "sh", "-c", "gunicorn ${GUNICORN_PARAMS} meertime.wsgi:application"]
