import sentry_sdk
from meertime.settings import env
from sentry_sdk.integrations.django import DjangoIntegration

SENTRY_DSN = env("SENTRY_DSN", default=None)
sentry_sdk.init(SENTRY_DSN, integrations=[DjangoIntegration()])
