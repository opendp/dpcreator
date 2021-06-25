from io import StringIO
import os
from unittest import skip

from django.contrib.auth import get_user_model
from django.test import TestCase, modify_settings, override_settings
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.core.management.base import CommandError
from django.core.management import call_command

from rest_framework.test import APIClient

from opendp_apps.model_helpers.msg_util import msg, msgt
from opendp_apps.cypress_utils import static_vals as cystatic


test_01_settings = override_settings(
    ROOT_URLCONF='opendp_project.urls_cypress',
    ALLOW_CYPRESS_ENDPOINT='cypress-in-ci-endpoint',
)

test_02_settings_no_url = override_settings(
    # ROOT_URLCONF='opendp_project.urls_cypress',
    ALLOW_CYPRESS_ENDPOINT='cypress-in-ci-endpoint',
)

test_03_settings_no_cypress_val = override_settings(
    ROOT_URLCONF='opendp_project.urls_cypress',
    # ALLOW_CYPRESS_ENDPOINT='cypress-in-ci-endpoint',
)

test_04_settings_bad_cypress_val = override_settings(
    ROOT_URLCONF='opendp_project.urls_cypress',
    ALLOW_CYPRESS_ENDPOINT='wrong-val-here',
)

class TestClearData(TestCase):


    def setUp(self):
        # test client
        self.client = APIClient()

        # Non-superuser
        self.user_obj_depositor, _created = get_user_model().objects.get_or_create(\
                                                    username='dv_depositor', is_superuser=False)

        # Superuser
        self.user_obj_admin, _created = get_user_model().objects.get_or_create(\
                                                    username='dev_admin', is_superuser=True)

    @test_01_settings
    def test_10_clear_data_success(self):
        """(10) Successfully clear the data"""
        msgt(self.test_10_clear_data_success.__doc__)


        with self.modify_settings(INSTALLED_APPS={
            'append': 'opendp_apps.cypress_utils'}):

            # set DJANGO_SETTINGS_MODULE
            os.environ['DJANGO_SETTINGS_MODULE'] = 'opendp_project.settings.cypress_settings'

            # log in with superuser
            self.client.force_login(self.user_obj_admin)

            clear_data_url = reverse('clear_test_data')
            jresp = self.client.get(clear_data_url)

            print(jresp.json())
            self.assertEquals(jresp.status_code, 200)

            # Test management command in the same context
            self.run_cmd_clear_test_data(expect_success=True)


    @test_01_settings
    def test_20_clear_data_fail_not_superuser(self):
        """(20) Fail, logged in but not superuser"""
        msgt(self.test_20_clear_data_fail_not_superuser.__doc__)


        with self.modify_settings(INSTALLED_APPS={
            'append': 'opendp_apps.cypress_utils'}):

            # set DJANGO_SETTINGS_MODULE
            os.environ['DJANGO_SETTINGS_MODULE'] = 'opendp_project.settings.cypress_settings'

            # log in with non-superuser
            self.client.force_login(self.user_obj_depositor)

            clear_data_url = reverse('clear_test_data')
            jresp = self.client.get(clear_data_url)

            #print(jresp.json())
            self.assertEquals(jresp.status_code, 404)

            # Test management command in the similar context
            # Except that it works b/c this is someone w/ access to the command line
            self.run_cmd_clear_test_data(expect_success=True)


    @test_01_settings
    def test_30_clear_data_fail_not_logged_in(self):
        """(30) Fail, not logged in"""
        msgt(self.test_30_clear_data_fail_not_logged_in.__doc__)


        with self.modify_settings(INSTALLED_APPS={
            'append': 'opendp_apps.cypress_utils'}):

            # set DJANGO_SETTINGS_MODULE
            os.environ['DJANGO_SETTINGS_MODULE'] = 'opendp_project.settings.cypress_settings'

            # Don't login

            clear_data_url = reverse('clear_test_data')
            jresp = self.client.get(clear_data_url)

            #print(jresp.json())
            self.assertEquals(jresp.status_code, 404)

            # Test management command in the similar context
            # Except that it works b/c this is someone w/ access to the command line
            self.run_cmd_clear_test_data(expect_success=True)



    @test_02_settings_no_url
    def test_40_clear_data_fail_no_url(self):
        """(40) url not available b/c ROOT_URLCONF incorrect"""
        msgt(self.test_40_clear_data_fail_no_url.__doc__)

        with self.modify_settings(INSTALLED_APPS={
            'append': 'opendp_apps.cypress_utils'}):

            # set DJANGO_SETTINGS_MODULE
            os.environ['DJANGO_SETTINGS_MODULE'] = 'opendp_project.settings.cypress_settings'

            # log in with superuser
            self.client.force_login(self.user_obj_admin)

            try:
                clear_data_url = reverse('clear_test_data')
            except NoReverseMatch as err_obj:
                self.assertEquals('NoReverseMatch', err_obj.__class__.__name__)

            # Test management command in the similar context
            # Except that it works b/c this is someone w/ access to the command line
            self.run_cmd_clear_test_data(expect_success=True)



    @test_01_settings
    def test_45_clear_data_fail_no_cypress_app(self):
        """(45) url not available b/c cypress app not in INSTALLED_APPS"""
        msgt(self.test_45_clear_data_fail_no_cypress_app.__doc__)

        # Don't add cypress to installed apps
        #with self.modify_settings(INSTALLED_APPS={
        #    'append': 'opendp_apps.cypress_utils'}):

        # set DJANGO_SETTINGS_MODULE
        os.environ['DJANGO_SETTINGS_MODULE'] = 'opendp_project.settings.cypress_settings'

        # log in with superuser
        self.client.force_login(self.user_obj_admin)

        try:
            clear_data_url = reverse('clear_test_data')
        except NoReverseMatch as err_obj:
            self.assertEquals('NoReverseMatch', err_obj.__class__.__name__)

        # Test management command in the same context
        self.run_cmd_clear_test_data(expect_success=False, **dict(expect_command_error=True))

    @test_03_settings_no_cypress_val
    def test_50_clear_data_fail_bad_cypress_val(self):
        """(50) fail b/c no ALLOW_CYPRESS_ENDPOINT value"""
        msgt(self.test_50_clear_data_fail_bad_cypress_val.__doc__)

        with self.modify_settings(INSTALLED_APPS={
            'append': 'opendp_apps.cypress_utils'}):

            # set DJANGO_SETTINGS_MODULE
            os.environ['DJANGO_SETTINGS_MODULE'] = 'opendp_project.settings.cypress_settings'

            # log in with superuser
            self.client.force_login(self.user_obj_admin)

            clear_data_url = reverse('clear_test_data')

            jresp = self.client.get(clear_data_url)

            self.assertEquals(jresp.status_code, 404)

            # Test management command in the same context
            self.run_cmd_clear_test_data(expect_success=False)


    @test_04_settings_bad_cypress_val
    def test_60_clear_data_fail_bad_cypress_val(self):
        """(60) fail b/c bad ALLOW_CYPRESS_ENDPOINT value"""
        msgt(self.test_60_clear_data_fail_bad_cypress_val.__doc__)

        with self.modify_settings(INSTALLED_APPS={
            'append': 'opendp_apps.cypress_utils'}):
            # set DJANGO_SETTINGS_MODULE
            os.environ['DJANGO_SETTINGS_MODULE'] = 'opendp_project.settings.cypress_settings'

            # log in with superuser
            self.client.force_login(self.user_obj_admin)

            clear_data_url = reverse('clear_test_data')

            jresp = self.client.get(clear_data_url)

            self.assertEquals(jresp.status_code, 404)

            # Test management command in the same context
            self.run_cmd_clear_test_data(expect_success=False)



    def run_cmd_clear_test_data(self, expect_success=False, **kwargs):
        """Run the management command 'clear_test_data'"""
        out = StringIO()
        cmd_output = None

        expect_command_error = kwargs.get('expect_command_error', False)

        try:
            call_command("clear_test_data",
                         *[],
                         stdout=out,
                         stderr=StringIO(),
                         **dict())
            cmd_output = out.getvalue()
        except CommandError as err_obj:
            if expect_command_error:
                self.assertEquals('CommandError', err_obj.__class__.__name__)
                return
            # Force an error, shouldn't have a CommandError
            print('(1b) ---')
            self.assertTrue(False)

        #print('cmd_output', cmd_output)
        if expect_success:
            self.assertTrue(cmd_output.find('Data deletion complete') > -1)
        else:
            print('-- cmd_output:', cmd_output)
            print('-- cystatic.MESSAGE_CLEAR_DATA_CMD_ERR:', cystatic.MESSAGE_CLEAR_DATA_CMD_ERR)
            self.assertTrue(cmd_output.find(cystatic.MESSAGE_CLEAR_DATA_CMD_ERR) > -1)
