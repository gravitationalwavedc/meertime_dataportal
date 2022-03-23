from django.apps import AppConfig


class UserManageConfig(AppConfig):
    name = 'user_manage'

    def ready(self):
        import user_manage.signals
