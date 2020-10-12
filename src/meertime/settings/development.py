from meertime.settings.settings import MIDDLEWARE, INSTALLED_APPS, BASE_DIR
import os

# Development Settings

DEBUG = True

# Enable query count check
MIDDLEWARE.append("querycount.middleware.QueryCountMiddleware")

# Enable API for local react app development
INSTALLED_APPS.append("corsheaders")
MIDDLEWARE.append("corsheaders.middleware.CorsMiddleware")

CORS_ORIGIN_ALLOW_ALL = True

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
