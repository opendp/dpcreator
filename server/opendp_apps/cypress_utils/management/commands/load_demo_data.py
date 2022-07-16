"""
Allow deletion of data in between cypress tests
"""
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from opendp_apps.cypress_utils import static_vals as cystatic
from opendp_apps.user.models import OpenDPUser

depositor_password = os.environ.get('USER_DEPOSITOR_PASSWORD')
analyst_password = os.environ.get('USER_ANALYST_PASSWORD')


class Command(BaseCommand):
    help = "Prepares data for demo / user testing"

    def handle(self, *args, **options):
        """Delete data in-between user tests"""

        # Important check!!
        if not settings.ALLOW_DEMO_LOADING:  # Do not remove this check
            self.stdout.write(self.style.ERROR(cystatic.MESSAGE_CLEAR_DATA_CMD_ERR))
            return

        depositor_user = OpenDPUser.objects.creata(username='dp_depositor',
                                                   first_name='DP',
                                                   last_name='Depositor',
                                                   email='test_depositor@opendp.org')
        depositor_user.set_password(depositor_password)

        analyst_user = OpenDPUser.objects.creata(username='dp_analyst',
                                                 first_name='DP',
                                                 last_name='Analyst',
                                                 email='test_analyst@opendp.org')
        analyst_user.set_password(analyst_password)

        # TODO: Add data file and pre-fill several of the DP Creator steps

