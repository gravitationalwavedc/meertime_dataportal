"""
This is a django-split-settings main file.
For more information read this:
https://github.com/sobolevn/django-split-settings
"""

import environ
from split_settings.tools import include, optional

# Set the evnironment variable
env = environ.Env()
ENV = env("ENV", default="")

# Read in either .env or .env.production
environ.Env.read_env(f".env{ENV}")

DEVELOPMENT_MODE = env("DEVELOPMENT_MODE", default=False)
ENABLE_SENTRY_DSN = env("SENTRY_DSN", default=False)

base_settings = [
    "settings.py",
    "logging.py",
    "database.py",
    "graphene.py",
    "authentication.py",
    "kronos_payload.py",
    "slack.py",
    "email.py",
    "cache.py",
    "file_download.py",
    # Optionally override some settings:
    optional("local.py"),
]

if DEVELOPMENT_MODE:
    base_settings.append("development.py")
    base_settings.append("django_debug_toolbar.py")

if ENABLE_SENTRY_DSN:
    base_settings.append("sentry_sdk.py")

# Include settings:
include(*base_settings)
