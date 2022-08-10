import os
from unittest import TestCase

from opendp_apps.profiler.tools.spss_reader import SpssReader


class TestSpssReader(TestCase):

    def test_read_sav(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'survey.sav')
        column_limit = 1
        spss_reader = SpssReader(file_path, column_limit=column_limit)
        df = spss_reader.read()
        self.assertEqual(spss_reader.meta.column_names[2:5], ['age', 'marital', 'child'])
        self.assertListEqual(list(df.columns), ['id'])

    def test_read_dta(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'golf.dta')
        column_limit = 2
        spss_reader = SpssReader(file_path, column_limit=column_limit)
        df = spss_reader.read()
        print(df)
        self.assertEqual(spss_reader.meta.column_names, ['score', 'age'])
        self.assertListEqual(list(df.columns), ['score', 'age'])
