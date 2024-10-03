from meertime.settings import env

if env("REDIS_SERVER", default=None):
    CACHE_BACKEND = "django_redis.cache.RedisCache"
else:
    CACHE_BACKEND = "django.core.cache.backends.dummy.DummyCache"


CACHES = {
    "default": {
        "BACKEND": CACHE_BACKEND,
        "LOCATION": env("REDIS_SERVER", default=""),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": env("REDIS_PASSWORD", default=""),
        },
    }
}
