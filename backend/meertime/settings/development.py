from meertime.settings.settings import MIDDLEWARE, INSTALLED_APPS, BASE_DIR

from meertime.settings import env
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

# uncomment this while doing development to view emails in console
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# set gmail settings True if using gmail's smtp
GMAIL_SMTP = env("GMAIL_SMTP", None)

# gmail smtp settings
if GMAIL_SMTP == "True":
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587

    DEFAULT_FROM_EMAIL = env("GMAIL_ACCOUNT")
    EMAIL_HOST_USER = env("GMAIL_ACCOUNT")
    EMAIL_HOST_PASSWORD = env("GMAIL_ACCOUNT_PASSWORD")

