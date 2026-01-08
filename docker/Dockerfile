# Multi-stage Dockerfile for MeerTime application

# =============================================================================
# Stage 1: Django base (common setup for builder and runtime)
# =============================================================================
FROM python:3.12-slim-trixie AS django-base

ENV \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.8.3 \
  GET_POETRY_IGNORE_DEPRECATION=1 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  PATH="/root/.local/bin:$PATH"

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
  && curl -sSL https://install.python-poetry.org | python3 \
  && poetry --version \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

RUN adduser web

COPY --chown=web:web ./backend/pyproject.toml ./backend/poetry.lock /code/

RUN poetry install --no-interaction --no-ansi

COPY ./backend /code/

# =============================================================================
# Stage 2: Django builder (collect static files)
# =============================================================================
FROM django-base AS django-builder

# Collect static files (this creates hashed filenames and staticfiles.json manifest)
RUN python manage.py collectstatic --noinput

# =============================================================================
# Stage 3: Django runtime
# =============================================================================
FROM django-base AS django

# Copy only the staticfiles.json manifest, not the actual static files
COPY --from=django-builder /static/staticfiles.json /static/staticfiles.json

ENV GUNICORN_PARAMS="-b 0.0.0.0:8000 --workers 8 --timeout 600"
CMD [ "sh", "-c", "python manage.py migrate --noinput && gunicorn ${GUNICORN_PARAMS} meertime.wsgi:application"]

# =============================================================================
# Stage 4: Cron service for django-post-office
# =============================================================================
FROM django-base AS cron

# Install cron
RUN apt-get update \
  && apt-get install --no-install-recommends -y cron \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Set up cron jobs for django-post-office and membership reminders
RUN echo "PYTHONBUFFERED=1" >> /etc/cron.d/crontab && \
    echo "PATH=${PATH}" >> /etc/cron.d/crontab && \
    echo "POETRY_VIRTUALENVS_CREATE=false" >> /etc/cron.d/crontab && \
    echo "* * * * * cd /code; python manage.py send_queued_mail > /proc/1/fd/1 2>/proc/1/fd/2" >> /etc/cron.d/crontab && \
    echo "0 * * * * cd /code; python manage.py send_membership_reminders > /proc/1/fd/1 2>/proc/1/fd/2" >> /etc/cron.d/crontab && \
    echo "0 1 * * * cd /code; python manage.py cleanup_mail --days=30 --delete-attachments > /proc/1/fd/1 2>/proc/1/fd/2" >> /etc/cron.d/crontab && \
    chmod 0644 /etc/cron.d/crontab && \
    /usr/bin/crontab /etc/cron.d/crontab

CMD ["cron", "-f"]

# =============================================================================
# Stage 6: Build React frontend
# =============================================================================
FROM node:18 AS react-builder

WORKDIR /app

RUN npm install -g pnpm

COPY ./frontend/package.json ./frontend/pnpm-lock.yaml /app/

RUN pnpm install

COPY ./frontend /app/

RUN pnpm run relay 
RUN pnpm run build

# =============================================================================
# Stage 7: React runtime (nginx)
# =============================================================================
FROM nginx:1.29 AS react

COPY --from=react-builder /app/dist /react_app/
COPY ./nginx/react_app.conf /etc/nginx/conf.d/nginx.conf

# =============================================================================
# Stage 8: Main nginx (serves static files and proxies)
# =============================================================================
FROM nginx:1.29 AS nginx

COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy static files from Django builder
COPY --from=django-builder /static /static
