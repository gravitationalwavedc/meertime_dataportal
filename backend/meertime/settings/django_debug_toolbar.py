from meertime.settings.settings import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS.append("debug_toolbar")
INSTALLED_APPS.append("graphiql_debug_toolbar")

MIDDLEWARE.append("graphiql_debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = ["127.0.0.1"]

SHOW_TOOLBAR_CALLBACK = True
