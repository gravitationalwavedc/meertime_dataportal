# This Dockerfile builds the MeerTime Django application for deployment on Kubernetes.

FROM python:3.8-slim-buster

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
  POETRY_VERSION=1.1.4 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  PATH="$PATH:/root/.poetry/bin"

# System dependencies:
RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    curl \
    gettext \
    git \
    wget \
    libmariadb-dev \
  # Installing `poetry` package manager:
  # https://github.com/python-poetry/poetry
  && curl -sSL 'https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py' | python \
  && poetry --version \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code 

COPY --chown=web:web ./backend/pyproject.toml ./backend/poetry.lock /code/

# support development_mode in docker
RUN if [ "${DEVELOPMENT_MODE}" = "True" ]; then poetry install --no-interation --no-ansi; else poetry install --no-dev --no-interaction --no-ansi; fi;

COPY ./backend /code/

EXPOSE 8000

ENV GUNICORN_PARAMS="-b 0.0.0.0:8000 --workers 8 --timeout 600"
CMD [ "sh", "-c", "gunicorn ${GUNICORN_PARAMS} meertime.wsgi:application"]
