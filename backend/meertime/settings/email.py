from meertime.settings import env

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_FROM = env("EMAIL_FROM", default="noreply@adacs.org")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT", default=25)
