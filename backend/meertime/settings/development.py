import os

from meertime.settings.settings import BASE_DIR, INSTALLED_APPS, MIDDLEWARE

# Development Settings

DEBUG = True

# Enable query count check
MIDDLEWARE.append("querycount.middleware.QueryCountMiddleware")

# Enable API for local react app development
INSTALLED_APPS.extend(["django_extensions", "corsheaders"])

MIDDLEWARE.append("corsheaders.middleware.CorsMiddleware")

CORS_ORIGIN_ALLOW_ALL = True

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

SITE_URL = "http://localhost:5173/"  # with a trailing slash

# Email settings for Development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Don't use the redis cache in local development.
# It's only currently used for django-cachalot so this shouldn't
# cause any issues.
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.dummy.DummyCache",
#         "LOCATION": "",
#         "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient", "PASSWORD": ""},
#     }
# }

SESSION_COOKIE_SECURE = False  # Set to False in development if not using HTTPS
CSRF_TRUSTED_ORIGINS = ["http://localhost:5173"]
