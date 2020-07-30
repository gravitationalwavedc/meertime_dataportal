import sentry_sdk
import os

SENTRY_INGEST = os.environ["SENTRY_INGEST"]

sentry_sdk.init(SENTRY_INGEST)
