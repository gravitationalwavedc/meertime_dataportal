import socket
from meertime.settings import env
from meertime.settings.settings import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS.append("debug_toolbar")
INSTALLED_APPS.append('graphiql_debug_toolbar')
# MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
MIDDLEWARE.append("graphiql_debug_toolbar.middleware.DebugToolbarMiddleware")
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [env("INTERNAL_IPS", default="127.0.0.1"), "10.0.2.2", "0.0.0.0", "localhost"]
SHOW_TOOLBAR_CALLBACK=True