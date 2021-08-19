from django.apps import AppConfig


class WebCacheConfig(AppConfig):
    name = 'web_cache'

    def ready(self):
        import web_cache.signals
