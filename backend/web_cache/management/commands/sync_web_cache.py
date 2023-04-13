from django.core.management.base import BaseCommand
from web_cache.management.commands._command_functions import sync_foldmode, sync_searchmode, sync_sessions


class Command(BaseCommand):
    help = "Sync the web cache data with the current database"

    def handle(self, *args, **options):
        sync_foldmode()
        sync_searchmode()
        sync_sessions()
