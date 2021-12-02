import pandas as pd

from os.path import abspath, dirname, join

from django.test import TestCase

from opendp_apps.profiler.variable_info import VariableInfoHandler

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')


class TestVariableInfoHandler(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.df = pd.read_csv(join(TEST_DATA_DIR, 'Fatigue_data.tab'), delimiter='\t')

    def test_run_profile_process(self):
        """Test VariableInfoHandler object"""
        print(self.test_run_profile_process.__doc__)
        variable_info_handler = VariableInfoHandler(self.df)
        profile = variable_info_handler.run_profile_process()

        self.assertEqual(profile['dataset']['rowCount'], 183)
        self.assertEqual(profile['dataset']['variableCount'], 24)
        self.assertEqual(len(profile['dataset']['variableOrder']), 24)
        self.assertEqual(len(profile['variables']), 24)
        self.assertDictEqual(profile['variables']['lrPupilCorrelation'], {'label': '',
                                                                          'sort_order': 23,
                                                                          'name': 'lrPupilCorrelation',
                                                                          'type': 'Float'
                                                                          })
        self.assertDictEqual(profile['variables']['Trial'], {'label': '',
                                                             'sort_order': 4,
                                                             'name': 'Trial',
                                                             'type': 'Integer'
                                                             })
        self.assertDictEqual(profile['variables']['Session'], {'label': '',
                                                               'sort_order': 2,
                                                               'name': 'Session',
                                                               'categories': [],
                                                               'type': 'Boolean'
                                                               })
