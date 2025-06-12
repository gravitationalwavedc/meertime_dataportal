import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from meertime.settings import env

SENTRY_DSN = env("SENTRY_DSN", default=None)
sentry_sdk.init(SENTRY_DSN, integrations=[DjangoIntegration()])
