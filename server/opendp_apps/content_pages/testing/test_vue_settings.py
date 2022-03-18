from rest_framework import status

from django.conf import settings
from django.test import TestCase, override_settings

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.content_pages import static_vals as cstatic
from opendp_apps.model_helpers.msg_util import msgt

_TEST_GOOGLE_ID = 'google-123'
_TEST_ADOBE_ID = 'pdf-abc'

class TestVueSettings(TestCase):
    """
    Test the vue settings API endpoint
    """

    def setUp(self):
        # test client
        self.client = APIClient()

    def check_epsilon_resp(self, jresp):
        """Note, MAX_EPSILON_OFFSET is not an env variables"""
        self.assertEqual(jresp["TOTAL_EPSILON_MIN"], settings.TOTAL_EPSILON_MIN)
        self.assertEqual(jresp["TOTAL_EPSILON_MAX"], settings.TOTAL_EPSILON_MAX)
        self.assertEqual(jresp["MAX_EPSILON_OFFSET"], astatic.MAX_EPSILON_OFFSET)

    @override_settings(VUE_APP_GOOGLE_CLIENT_ID=_TEST_GOOGLE_ID,
                       VUE_APP_ADOBE_PDF_CLIENT_ID=_TEST_ADOBE_ID)
    def test_10_vue_settings_set_variables(self):
        """(10) The variables are set to strings"""
        msgt(self.test_10_vue_settings_set_variables.__doc__)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('vue-settings-list')

        resp = self.client.get(url, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        jresp = resp.json()
        self.assertEqual(jresp[cstatic.KEY_VUE_APP_GOOGLE_CLIENT_ID], _TEST_GOOGLE_ID)
        self.assertEqual(jresp[cstatic.KEY_VUE_APP_ADOBE_PDF_CLIENT_ID], _TEST_ADOBE_ID)
        self.check_epsilon_resp(jresp)

    @override_settings(VUE_APP_GOOGLE_CLIENT_ID=None,
                       VUE_APP_ADOBE_PDF_CLIENT_ID=_TEST_ADOBE_ID)
    def test_20_vue_settings_googleid_none(self):
        """(20) Set the VUE_APP_GOOGLE_CLIENT_ID to None """
        msgt(self.test_20_vue_settings_googleid_none.__doc__)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('vue-settings-list')

        resp = self.client.get(url, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        jresp = resp.json()
        self.assertEqual(jresp[cstatic.KEY_VUE_APP_GOOGLE_CLIENT_ID], None)
        self.assertEqual(jresp[cstatic.KEY_VUE_APP_ADOBE_PDF_CLIENT_ID], _TEST_ADOBE_ID)
        self.check_epsilon_resp(jresp)

    @override_settings(VUE_APP_GOOGLE_CLIENT_ID=_TEST_GOOGLE_ID,
                       VUE_APP_ADOBE_PDF_CLIENT_ID=None)
    def test_30_vue_settings_set_variables(self):
        """(30) VUE_APP_ADOBE_PDF_CLIENT_ID is None"""
        msgt(self.test_30_vue_settings_set_variables.__doc__)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('vue-settings-list')

        resp = self.client.get(url, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        jresp = resp.json()
        self.assertEqual(jresp[cstatic.KEY_VUE_APP_GOOGLE_CLIENT_ID], _TEST_GOOGLE_ID)
        self.assertEqual(jresp[cstatic.KEY_VUE_APP_ADOBE_PDF_CLIENT_ID], None)
        self.check_epsilon_resp(jresp)

    @override_settings(VUE_APP_GOOGLE_CLIENT_ID=_TEST_GOOGLE_ID,
                       VUE_APP_ADOBE_PDF_CLIENT_ID=_TEST_ADOBE_ID,
                       TOTAL_EPSILON_MIN=0.01,
                       TOTAL_EPSILON_MAX=0.9,
                       )
    def test_40_vue_settings_set_variables(self):
        """(40) Test epsilon settings"""
        msgt(self.test_40_vue_settings_set_variables.__doc__)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('vue-settings-list')

        resp = self.client.get(url, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        jresp = resp.json()
        self.assertEqual(jresp[cstatic.KEY_VUE_APP_GOOGLE_CLIENT_ID], _TEST_GOOGLE_ID)
        self.assertEqual(jresp[cstatic.KEY_VUE_APP_ADOBE_PDF_CLIENT_ID], _TEST_ADOBE_ID)

        self.assertEqual(jresp['TOTAL_EPSILON_MIN'], 0.01)
        self.assertEqual(jresp['TOTAL_EPSILON_MAX'], 0.9)
