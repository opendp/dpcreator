"""
Test of epsilon addition and offsetting floating point anomaly
"""
from unittest import skip

from django.test import TestCase

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.model_helpers.msg_util import msgt


@skip('Reconfiguring for analyst mode')
class TestEpsilonMax(TestCase):

    def setUp(self):
        self.epsilon_budget_1 = 1.0
        self.epsilon_budget_0_5 = 0.5
        self.epsilon_budget_0_1 = 0.1
        self.budgets_to_test = [self.epsilon_budget_1,
                                self.epsilon_budget_0_5,
                                self.epsilon_budget_0_1]
        self.num_budget_1_stats_that_fail = [
            9, 11, 18, 20, 21, 25, 35, 36, 39, 40, 41, 42, 43, 45, 47, 48, 49, 50, 51, 52,
            55, 56, 57, 58, 60, 61, 67, 73, 76, 77, 81, 82, 83, 86, 89, 92, 95, 98, 100, 101,
            108, 111, 113, 114, 122, 123, 125, 129, 131, 133, 134, 135, 138, 141, 145, 146,
            147, 148, 150]

    def test_10_epsilon_check(self):
        """
        Test that the epsilon "offset" works.
        Known error: if an epsilon of 1.0 is split evenly between 9 stats,
           adding the separate epsilons "0.1111111111111111" together gives
           1.0000000000000002.
           e.g.  0.1111111111111111 added (not multipled) 9x = 1.0000000000000002

        Fix: sum the epsilons and subtract 1e-14** before comparing the sum to the max_epsilon_budget
           ** astatic.MAX_EPSILON_OFFSET

        Test up to 150 stats and max budgets of 1.0 and 0.5
        """
        msgt(self.test_10_epsilon_check.__doc__)

        fail_nums = []
        for max_epsilon_budget in self.budgets_to_test:
            num_stats = 150 + 1
            msgt(f'Try budget: {max_epsilon_budget} with up to {num_stats - 1} stats')
            for num_stats in range(1, num_stats):
                epsilon_per_stat = max_epsilon_budget / num_stats

                # print((f'\n\nnum_stats/budget.epsilon_per_stat: '
                #       f' {num_stats}/{max_epsilon_budget}/{epsilon_per_stat}'))

                summed_stats = 0
                for n in range(num_stats):
                    summed_stats += epsilon_per_stat

                # test case of 0.1111111111111111 added (not multipled) 9x = 1.0000000000000002
                #
                if num_stats in self.num_budget_1_stats_that_fail and max_epsilon_budget == self.epsilon_budget_1:
                    self.assertFalse(summed_stats <= max_epsilon_budget)

                self.assertTrue((summed_stats - astatic.MAX_EPSILON_OFFSET) <= max_epsilon_budget)
