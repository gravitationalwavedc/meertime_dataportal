import freezegun

freezegun.configure(extend_ignore_list=["cachalot", "django.contrib.auth", "django.contrib.sessions"])

# Decorator-level frozen time can otherwise make login sessions expire in the past.
SESSION_COOKIE_AGE = 60 * 60 * 24 * 365 * 100
