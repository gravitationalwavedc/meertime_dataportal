from django.apps import AppConfig


class DataportalConfig(AppConfig):
    name = "dataportal"

    def ready(self):
        import dataportal.signals  # noqa
