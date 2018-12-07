from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run periodic tasks'

    def handle(self, *args, **options):
        pass
