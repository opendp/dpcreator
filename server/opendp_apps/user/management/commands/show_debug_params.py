import os
from django.core.management.base import BaseCommand

from django.conf import settings

class Command(BaseCommand):
    """
    This command expects a json file in the server/ directory
    """
    def handle(self, *args, **options):
        print('BASE_DIR', settings.BASE_DIR)
        print('STATIC_ROOT', settings.STATIC_ROOT)
        for af in os.listdir(settings.STATIC_ROOT):
            print('static root listing:', af)
