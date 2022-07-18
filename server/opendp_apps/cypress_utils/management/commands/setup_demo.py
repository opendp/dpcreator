"""
Allow deletion of data in between cypress tests
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand

from opendp_apps.cypress_utils.management.commands.demo_loading_decorator import check_allow_demo_loading


class Command(BaseCommand):
    help = "Prepares data for demo / user testing"

    @check_allow_demo_loading  # Do not remove this check
    def handle(self, *args, **options):
        """Delete data in-between user tests"""
        call_command('clear_test_data')
        call_command('load_demo_data')

