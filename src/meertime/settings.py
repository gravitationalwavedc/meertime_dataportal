import logging
import os
import environ

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False

env = environ.Env(DEBUG=(bool, False), ADMIN_ENABLED=(bool, False))
ENV = env("ENV", default="")
environ.Env.read_env(f".env{ENV}")

DEBUG = env("DEBUG")
USE_TOOLBAR_IN_DEBUG = env("USE_TOOLBAR_IN_DEBUG", default=True)
USE_CPROFILER_IN_DEBUG = env("USE_CPROFILER_IN_DEBUG", default=False)

logger.info(f"DEBUG is set to {DEBUG}")
ADMIN_ENABLED = env("ADMIN_ENABLED")
logger.info(f"ADMIN_ENABLED is set to {ADMIN_ENABLED}")

SENTRY_DSN = env("SENTRY_DSN", default=None)

if SENTRY_DSN and DEBUG == False:
    sentry_sdk.init(SENTRY_DSN, integrations=[DjangoIntegration()])
else:
    logger.warn("Sentry has not been set")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "dataportal.apps.DataportalConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mathfilters",
    "graphene_django",
]

if DEBUG and USE_TOOLBAR_IN_DEBUG:
    INSTALLED_APPS.append("debug_toolbar")

if DEBUG:
    INSTALLED_APPS.append("corsheaders")

GRAPHENE = {
    "SCHEMA": "meertime.schema.schema",
    "SCHEMA_OUTPUT": "./frontend/data/schema.json",
    "MIDDLEWARE": ["graphql_jwt.middleware.JSONWebTokenMiddleware"],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    if USE_TOOLBAR_IN_DEBUG:
        INTERNAL_IPS = env("INTERNAL_IPS", default="127.0.0.1")
        MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    MIDDLEWARE.append("querycount.middleware.QueryCountMiddleware")
    MIDDLEWARE.append("corsheaders.middleware.CorsMiddleware")
    CORS_ORIGIN_ALLOW_ALL = True
    if USE_CPROFILER_IN_DEBUG:
        DJANGO_CPROFILE_MIDDLEWARE_REQUIRE_STAFF = False
        MIDDLEWARE.append("django_cprofile_middleware.middleware.ProfilerMiddleware")

ROOT_URLCONF = "meertime.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "meertime.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("MYSQL_DATABASE"),
        "USER": env("MYSQL_USER"),
        "PASSWORD": env("MYSQL_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT", default=3306),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 7,},},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

AUTHENTICATION_BACKENDS = ["graphql_jwt.backends.JSONWebTokenBackend", "django.contrib.auth.backends.ModelBackend"]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = "/static/"
STATIC_URL = "/static/"

LOGIN_REDIRECT_URL = "/MeerTime"
