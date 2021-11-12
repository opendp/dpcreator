import numpy as np
import pandas as pd

from django.test import TestCase

from opendp_apps.profiler.preprocess_runner import PreprocessRunner


class TestPreprocessRunner(TestCase):

    maxDiff = None

    def setUp(self):
        self.df = pd.DataFrame({'a': range(0, 100),
                                'b': np.arange(0.0, 100.0),
                                'c': [True if x > 0.5 else False for x in np.random.rand(100)]})

    def test(self):
        prunner = PreprocessRunner(self.df)
        final_dict = prunner.get_final_dict()
        self.assertEqual(final_dict['variables']['a']['binary'], False)
        self.assertEqual(final_dict['variables']['a']['numchar'], 'numeric')

        self.assertEqual(final_dict['variables']['b']['binary'], False)
        self.assertEqual(final_dict['variables']['b']['numchar'], 'numeric')

        self.assertEqual(final_dict['variables']['c']['binary'], True)
        self.assertEqual(final_dict['variables']['c']['numchar'], 'character')

