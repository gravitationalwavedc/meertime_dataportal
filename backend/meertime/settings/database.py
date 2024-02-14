from meertime.settings import env

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("POSTGRES_DATABASE"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "PORT": env("POSTGRES_PORT", default=5432),
        "HOST": env("DB_HOST"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
