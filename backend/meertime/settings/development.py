from meertime.settings.settings import MIDDLEWARE, INSTALLED_APPS, BASE_DIR
import os

# Development Settings

DEBUG = True

# Enable query count check
MIDDLEWARE.append("querycount.middleware.QueryCountMiddleware")

# Enable API for local react app development
INSTALLED_APPS.extend(["django_extensions", "corsheaders"])

MIDDLEWARE.append("corsheaders.middleware.CorsMiddleware")

CORS_ORIGIN_ALLOW_ALL = True

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

SITE_URL = 'http://localhost:3000/'  # with a trailing slash

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
