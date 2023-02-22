from meertime.settings import env

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("MYSQL_DATABASE"),
        "USER": env("MYSQL_USER_2"),
        "PASSWORD": env("MYSQL_PASSWORD_2"),
        "HOST": env("DB_HOST"),
        "PORT": env("MYSQL_PORT", default=3306),
    }
}
