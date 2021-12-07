from os.path import abspath, dirname, join
import datetime
# from unittest import skip

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from opendp_apps.banner_messages.models import BannerMessage
from opendp_apps.banner_messages import static_vals as bstatic
from opendp_apps.model_helpers.msg_util import msgt


CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(CURRENT_DIR), 'test_files')


class BannerMessageTest(TestCase):

    def setUp(self):

        # test client
        self.client = APIClient()

        # Regular banner
        #
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

        bparams1 = dict(name='Demo site',
                        active=True,
                        type=bstatic.BANNER_TYPE_WARNING,
                        sort_order=1,
                        editor=self.user_obj,
                        content='This is a Demo site. <b>Do not use sensitive data</b>.')
        self.banner1 = BannerMessage(**bparams1)
        self.banner1.save()

        # Timed banner
        #
        self.current_time = timezone.now()
        self.yesterday = self.current_time + datetime.timedelta(days=-1)
        self.next_day = self.current_time + datetime.timedelta(days=1)

        bparams2 = dict(name='Demo site',
                        active=True,
                        type=bstatic.BANNER_TYPE_INFORMATIONAL,
                        sort_order=5,
                        editor=self.user_obj,
                        content=f'The site will be down until {self.next_day}.',
                        is_timed_message=True,
                        view_start_time=self.yesterday,
                        view_stop_time=self.next_day)
        self.banner2 = BannerMessage(**bparams2)
        self.banner2.save()

    def test_10_basic_banner_check(self):
        """(10) Basic banner check"""
        msgt(self.test_10_basic_banner_check.__doc__)

        banners = BannerMessage.objects.all()

        # two banners
        self.assertTrue(banners.count() == 2)

        # time window is valid
        self.assertTrue(self.banner2.is_current_time_window())

        # Get a queryset of active banners
        qs_banners = BannerMessage.get_active_banners()
        self.assertTrue(qs_banners.count() == 2)

    def test_15_banner_timing(self):
        """(15) banner timing"""
        msgt(self.test_15_banner_timing.__doc__)

        # test window with times outside the window
        #
        three_days_ago = self.current_time + datetime.timedelta(days=-3)
        self.assertFalse(self.banner2.is_current_time_window(three_days_ago))

        next_week = self.current_time + datetime.timedelta(days=7)
        self.assertFalse(self.banner2.is_current_time_window(next_week))

        # Get a queryset of active banners where the current time is out of range
        #   for the timed banners
        #
        self.assertTrue(BannerMessage.get_active_banners(three_days_ago).count() == 1)
        self.assertTrue(BannerMessage.get_active_banners(next_week).count() == 1)

        # Set bad timing for banner
        #
        self.banner2.view_start_time = self.next_day
        self.banner2.view_stop_time = self.yesterday

        with self.assertRaises(ValueError):
            self.banner2.save()

    def get_banner_messages_via_api(self, expected_count=None) -> {}:
        """Return the API JSON results for other tests"""
        response = self.client.get('/api/banner-messages/')
        self.assertEqual(response.status_code, 200)
        banner_info = response.json()

        if expected_count:
            self.assertTrue(banner_info['count'], expected_count)

        return banner_info

    def test_20_banner_api(self):
        """(20) Access the Banner messages via API"""
        msgt(self.test_20_banner_api.__doc__)

        banner_info = self.get_banner_messages_via_api(2)

        # Check the banner count and responses
        #
        self.assertEqual(banner_info['count'], 2)
        self.assertEqual(banner_info['results'][0]['type'], bstatic.BANNER_TYPE_WARNING)
        self.assertEqual(banner_info['results'][1]['type'], bstatic.BANNER_TYPE_INFORMATIONAL)

        # Flip the sorting order
        #
        self.banner1.sort_order = 100
        self.banner1.save()
        banner_info = self.get_banner_messages_via_api(2)
        self.assertEqual(banner_info['count'], 2)
        self.assertEqual(banner_info['results'][0]['type'], bstatic.BANNER_TYPE_INFORMATIONAL)
        self.assertEqual(banner_info['results'][1]['type'], bstatic.BANNER_TYPE_WARNING)

        # Set banners to inactive
        #
        self.banner1.save_as_inactive()
        self.banner2.save_as_inactive()

        banner_info = self.get_banner_messages_via_api(0)

