from django.test import override_settings
from rest_framework import status

from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.model_helpers.msg_util import msgt
from django.contrib.auth import get_user_model


class TestAnalysisPlanView(StatSpecTestCase):

    def setUp(self):
        super().setUp()

    @override_settings(ALLOW_RELEASE_DELETION=False)
    def test_010_delete_without_release_info(self):
        """(10) Test deleting an AnalysisPlan with a ReleaseInfo--disallowed"""
        msgt(self.test_010_delete_without_release_info.__doc__)

        new_plan = self.retrieve_new_plan()

        delete_url = f'{self.API_PREFIX}{new_plan.object_id}/'

        self.client.force_login(self.user_obj)
        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AnalysisPlan.objects.count(), 0)

    @override_settings(ALLOW_RELEASE_DELETION=False)
    def test_020_delete_with_release_info(self):
        """(20) Test deleting an AnalysisPlan without a ReleaseInfo"""
        msgt(self.test_020_delete_with_release_info.__doc__)

        new_plan = self.retrieve_new_plan()

        release_info = ReleaseInfo.objects.create(
            dataset=new_plan.dataset,
            epsilon_used=0.0,
            dp_release={}
        )
        release_info.save()

        new_plan.release_info = release_info
        new_plan.save()

        delete_url = f'{self.API_PREFIX}{new_plan.object_id}/'

        self.client.force_login(self.user_obj)
        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(AnalysisPlan.objects.count(), 1)

    @override_settings(ALLOW_RELEASE_DELETION=False)
    def test_030_delete_with_release_info_wrong_user(self):
        """(30) Test deleting an AnalysisPlan with the wrong user--disallowed"""
        msgt(self.test_030_delete_with_release_info_wrong_user.__doc__)

        new_plan = self.retrieve_new_plan()

        # Make unauthorized user
        #
        unauth_user_params = dict(username='jgemstone',
                                  email='jgemstone@ridiculous.edu',
                                  first_name='Judy',
                                  last_name='Gemstone')

        self.unauth_user, _created = get_user_model().objects.get_or_create(**unauth_user_params)

        # Attempt delete with unauthorized user
        #
        self.client.force_login(self.unauth_user)

        delete_url = f'{self.API_PREFIX}{new_plan.object_id}/'
        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(AnalysisPlan.objects.count(), 1)

        # Now delete with the correct user
        #
        self.client.force_login(self.user_obj)
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AnalysisPlan.objects.count(), 0)

    @override_settings(ALLOW_RELEASE_DELETION=False)
    def test_040_delete_without_logging_in(self):
        """(40) Test deleting an AnalysisPlan without logging in--disallowed"""
        msgt(self.test_040_delete_without_logging_in.__doc__)

        new_plan = self.retrieve_new_plan()

        delete_url = f'{self.API_PREFIX}{new_plan.object_id}/'
        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(AnalysisPlan.objects.count(), 1)
        
