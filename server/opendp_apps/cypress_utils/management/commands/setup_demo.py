"""
Allow deletion of data in between cypress tests
"""
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from opendp_apps.cypress_utils import static_vals as cystatic


class Command(BaseCommand):
    help = "Prepares data for demo / user testing"

    def handle(self, *args, **options):
        """Delete data in-between user tests"""

        # Important check!!
        if not settings.ALLOW_DEMO_LOADING:  # Do not remove this check
            self.stdout.write(self.style.ERROR(cystatic.MESSAGE_CLEAR_DATA_CMD_ERR))
            return

        call_command('clear_test_data')
        call_command('load_demo_data')

