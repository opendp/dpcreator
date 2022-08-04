from django.test.testcases import TestCase

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.tools.dp_spec_error import DPSpecError
from opendp_apps.model_helpers.msg_util import msgt


class DPSpecErrorTest(TestCase):
    """Some tests for the DPSpecError"""

    def setUp(self):
        """Some reusable info"""
        self.spec_props = {'variable': 'Income',
                           'col_index': 3,
                           'statistic': astatic.DP_MEAN,
                           'dataset_size': 10_000,
                           'epsilon': 1.0,
                           'delta': 0.0,
                           'cl': astatic.CL_95,
                           # 'accuracy': None,
                           'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                           'fixed_value': '45_000',
                           'variable_info': {'min': 14_000,
                                             'max': 2_500_000,
                                             'type': 'Float', },
                           }

    def test_10_min_spec_err(self):
        """(10) Test minimal DPSpecError"""
        msgt(self.test_10_min_spec_err.__doc__)

        min_spec_props = dict(error_message='This is a DPSpecError with bare minimal info')

        dp_spec = DPSpecError(min_spec_props)
        self.assertFalse(dp_spec.is_chain_valid())
        self.assertTrue(dp_spec.has_error())

        print(dp_spec.get_error_msg_dict())
        self.assertEqual(dp_spec.get_error_msg_dict()['valid'], False)

    def test_20_min_spec_err(self):
        """(10) Test DPSpecError with data and error"""
        msgt(self.test_20_min_spec_err.__doc__)

        self.spec_props['error_message'] = 'This is an error combined with data'
        dp_spec = DPSpecError(self.spec_props)
        self.assertFalse(dp_spec.is_chain_valid())
        self.assertTrue(dp_spec.has_error())

        print(dp_spec.get_error_msg_dict())
        self.assertEqual(dp_spec.get_error_msg_dict()['valid'], False)

    def test_30_fail_empty_props(self):
        """(30) Fail with empty constructor"""
        #   Needs at least 'error_message':
        #     `spec = DPSpecError(error_message="Something wrong")`
        msgt(self.test_30_fail_empty_props.__doc__)

        with self.assertRaises(AssertionError) as context:
            DPSpecError({})

        self.assertEqual(str(context.exception), DPSpecError.ERR_MSG_REQUIRED_PROPS)
