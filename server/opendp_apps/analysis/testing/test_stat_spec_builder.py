from os.path import abspath, dirname, join

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from django.test import TestCase

from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.stat_spec_builder import StatSpecBuilder


class TestStatSpecBuilder(TestCase):
    fixtures = ['test_dataset_data_001.json']

    def setUp(self):
        self.max_epsilon = 1

    def check_redistribute_success(self, success, dp_stats_updated, max_epsilon=1):
        """Convenience method to test results"""
        self.assertTrue(success)
        # print('dp_stats_updated: ', dp_stats_updated)

        total_epsilon = sum(stat['epsilon'] for stat in dp_stats_updated) + astatic.MAX_EPSILON_OFFSET
        print('total_epsilon: ', total_epsilon)
        self.assertTrue(total_epsilon <= max_epsilon)

    def test_10_redistribute_epsilon(self):
        """Test that redistribute epsilon works"""
        msgt(self.test_10_redistribute_epsilon.__doc__)

        dp_statistics = [
            {'locked': True, 'epsilon': 0.40},
            {'locked': False, 'epsilon': 0.3},
            {'locked': False, 'epsilon': 0.3},
            {'locked': False, 'epsilon': 0.1, 'auto_generated': True},
        ]
        max_epsilon = 1

        success, dp_stats_updated = StatSpecBuilder.redistribute_epsilon(max_epsilon, dp_statistics)
        self.check_redistribute_success(success, dp_stats_updated)

    def test_20_redistribute_epsilon(self):
        """Test that redistribute epsilon works"""
        msgt(self.test_20_redistribute_epsilon.__doc__)

        dp_statistics = [
            {'locked': False, 'epsilon': 0.1},
            {'locked': False, 'epsilon': 0.1},
            {'locked': False, 'epsilon': 0.1},
            {'locked': False, 'epsilon': 0.1},
            {'locked': False, 'epsilon': 0.1},
            {'locked': False, 'epsilon': 0.1},
            {'locked': False, 'epsilon': 0.1},
            {'locked': False, 'epsilon': 0.1},
            {'locked': False, 'epsilon': 0.1},
            {'locked': False, 'epsilon': 0.1},
            {'locked': False, 'epsilon': 0.1, 'auto_generated': True},
        ]
        max_epsilon = 1

        success, dp_stats_updated = StatSpecBuilder.redistribute_epsilon(max_epsilon, dp_statistics)
        self.check_redistribute_success(success, dp_stats_updated)

    def test_30_redistribute_epsilon_fail(self):
        """Test that redistribute epsilon lock check works"""
        msgt(self.test_30_redistribute_epsilon_fail.__doc__)

        dp_statistics = [
            {'locked': True, 'epsilon': 0.5},
            {'locked': True, 'epsilon': 0.5},
            {'locked': False, 'epsilon': 0.1, 'auto_generated': True},
        ]
        max_epsilon = 1

        success, dp_stats_or_err_msg = StatSpecBuilder.redistribute_epsilon(max_epsilon, dp_statistics)

        self.assertFalse(success)
        self.assertEqual(dp_stats_or_err_msg, astatic.ERR_MSG_BAD_TOTAL_LOCKED_EPSILON)

    def test_40_redistribute_epsilon(self):
        """Test that redistribute epsilon lock check works"""
        msgt(self.test_40_redistribute_epsilon.__doc__)

        dp_statistics = [
            {'locked': False, 'epsilon': 1},
            {'locked': False, 'epsilon': 0.1, 'auto_generated': True},
        ]
        max_epsilon = 1

        success, dp_stats_updated = StatSpecBuilder.redistribute_epsilon(max_epsilon, dp_statistics)
        self.check_redistribute_success(success, dp_stats_updated)
