from django.core.management.base import BaseCommand
from web_cache.management.commands._command_functions import sync_sessions


class Command(BaseCommand):
    help = 'Sync the web cache session data with the current database'

    def handle(self, *args, **options):
        sync_sessions()
