from django.core.management.base import BaseCommand

from user_manage.management.commands._command_functions import notify_provisional_users
from utils.constants import UserRole


class Command(BaseCommand):
    help = "Notify the provisional users to activate their accounts"

    def handle(self, *args, **options):
        notify_provisional_users(
            filename="unrestricted_user_emails.txt",
            role=UserRole.UNRESTRICTED.value,
        )
