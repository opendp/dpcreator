"""
Test of epsilon addition and offsetting floating point anomaly
"""
from django.test import TestCase

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.tools.bin_edge_helper import BinEdgeHelper
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.utils.extra_validators import \
    (VALIDATE_MSG_MORE_BINS_THAN_VALUES,
     VALIDATE_MSG_TWO_EDGES_MINIMUM)


class TestBinEdgeHelper(TestCase):

    def test_10_working_edges(self):
        """(10) Edges work"""
        msgt(self.test_10_working_edges.__doc__)

        min_val = 1
        max_val = 100
        number_of_bins = 5
        beh = BinEdgeHelper(min_val, max_val, number_of_bins)
        self.assertFalse(beh.has_error())

        edge_info = beh.as_json()

        # Check edges
        expected_edges = [1, 26, 50, 75, 101]
        self.assertEqual(expected_edges, edge_info['edges'])

        # Check buckets
        expected_buckets = ["[1, 25]", "[26, 49]", "[50, 74]", "[75, 100]", "uncategorized"]
        self.assertEqual(expected_buckets, edge_info['buckets'], )

        self.assertEqual(min_val, edge_info['inputs']['min'], )
        self.assertEqual(max_val, edge_info['inputs']['max'], )
        self.assertEqual(number_of_bins, edge_info['inputs']['number_of_bins'])

    def test_20_bad_inputs(self):
        """(20) Bad inputs"""
        msgt(self.test_20_bad_inputs.__doc__)

        # min > max
        beh = BinEdgeHelper(50, 1, 5)
        print(beh.get_err_msg())
        self.assertTrue(beh.has_error())
        self.assertTrue(beh.get_err_msg().find(astatic.ERR_MAX_NOT_GREATER_THAN_MIN) > -1)

        # too many bins
        beh = BinEdgeHelper(1, 50, 51)
        print(beh.get_err_msg())
        self.assertTrue(beh.has_error())
        self.assertTrue(beh.get_err_msg().find(VALIDATE_MSG_MORE_BINS_THAN_VALUES) > -1)

        # too few edges
        beh = BinEdgeHelper(1, 50, 1)
        print(beh.get_err_msg())
        self.assertTrue(beh.has_error())
        self.assertTrue(beh.get_err_msg().find(VALIDATE_MSG_TWO_EDGES_MINIMUM) > -1)
