from meertime.settings import env
from meertime.settings.settings import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS.append("debug_toolbar")
MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = env("INTERNAL_IPS", default="127.0.0.1")
