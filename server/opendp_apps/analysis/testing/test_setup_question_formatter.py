"""
Test of epsilon addition and offsetting floating point anomaly
"""
from django.test import TestCase

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.analysis.setup_question_formatter import SetupQuestionFormatter
from opendp_apps.model_helpers.msg_util import msgt


class TestSetupQuestionFormatter(TestCase):

    def setUp(self):
        self.params_01_qs_set1 = {"radio_best_describes": "notHarmButConfidential",
                                  "radio_only_one_individual_per_row": "yes",
                                  "radio_depend_on_private_information": "yes"}
        self.params_01_qs_set2 = {"secret_sample": "yes",
                                  "population_size": "1000000",
                                  "observations_number_can_be_public": "yes"}

        self.deposit_info1 = DepositorSetupInfo(**{'dataset_questions': self.params_01_qs_set1,
                                                   'epsilon_questions': self.params_01_qs_set2})

        self.params_02_qs_set1 = {"radio_best_describes": "notHarmButConfidential",
                                  "radio_only_one_individual_per_row": "yes",
                                  "radio_depend_on_private_information": "yes"}
        self.params_02_qs_set2 = {"secret_sample": "no",
                                  "observations_number_can_be_public": "yes"}

        self.deposit_info2 = DepositorSetupInfo(**{'dataset_questions': self.params_02_qs_set1,
                                                   'epsilon_questions': self.params_02_qs_set2})

    def test_10_good_format(self):
        """Test that the formatter works correctly"""
        msgt(self.test_10_good_format.__doc__)

        util = SetupQuestionFormatter(self.deposit_info1)

        fmt_dict = util.as_dict()
        print(util.as_json())

        self.assertEqual(len(fmt_dict), 5)

        self.assertEqual(fmt_dict[1]['attribute'], astatic.SETUP_Q_02_ATTR)

        self.assertEqual(fmt_dict[1]['privacy_params'],
                         {"epsilon": 1, "delta": 5})

        self.assertEqual(fmt_dict[3]['population_size'], "1000000")
