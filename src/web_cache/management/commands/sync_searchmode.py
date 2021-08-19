from django.core.management.base import BaseCommand
from web_cache.management.commands._command_functions import sync_searchmode


class Command(BaseCommand):
    help = 'Sync the web cache searchmode data with the current database'

    def handle(self, *args, **options):
        sync_searchmode()
