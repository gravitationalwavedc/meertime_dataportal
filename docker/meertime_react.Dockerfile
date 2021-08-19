# Build the backend to generate the schema.json file
FROM python:3.8-slim-buster as backend

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
  PATH="$PATH:/root/.poetry/bin" \
  DEVELOPMENT_MODE=False

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

RUN poetry install --no-dev --no-interaction --no-ansi

COPY ./backend /code/

RUN python manage.py graphql_schema --out=./schema.json


# Build the react app to generate a clean production build
FROM node:12.14.1-buster as build

WORKDIR /app

COPY ./frontend/package*.json /app/

RUN npm install

COPY ./frontend /app/
COPY --from=backend /code/schema.json /app/data/

RUN npm run relay 
RUN npm run build


# Run the app
FROM nginx:1.17.8

COPY --from=build /app/build /react_app/ 
ADD ./nginx/react_app.conf /etc/nginx/conf.d/nginx.conf

EXPOSE 3000
