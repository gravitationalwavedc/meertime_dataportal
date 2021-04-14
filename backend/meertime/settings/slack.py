from meertime.settings import env

SLACK_WEBHOOK = env("SLACK_WEBHOOK", default=None)
