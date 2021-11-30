from os.path import abspath, dirname, isfile, join

from opendp_apps.profiler.csv_reader import DelimiterNotFoundException

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

import json

from django.test import TestCase
from django.conf import settings
from django.core.files import File

from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler import tasks as profiler_tasks
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.profiler.csv_reader import ColumnLimitLessThanOne

from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.analysis.models import DepositorSetupInfo
from django.core.serializers.json import DjangoJSONEncoder


class ProfilerTest(TestCase):

    fixtures = ['test_profiler_data_001.json']

    def setUp(self):
        """Used for multiple tests"""
        self.ds_01_object_id = "9255c067-e435-43bd-8af1-33a6987ffc9b"
        """
        # test client
        self.client = Client()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

        self.client.force_login(self.user_obj)

        self.mock_params = ManifestTestParams.objects.filter(use_mock_dv_api=True).first()
        """

    def profile_good_file(self, filename, num_features_orig, num_features_profile, num_rows, **kwargs):
        """Used by multiple tests...."""

        # File to profile
        #
        filepath1 = join(TEST_DATA_DIR, filename)
        self.assertTrue(isfile(filepath1))

        # Run profiler
        #
        # kwargs[pstatic.KW_MAX_NUM_FEATURES] = num_features_orig

        profiler = profiler_tasks.run_profile_by_filepath(filepath1, **kwargs)

        # Shouldn't have errors
        if profiler.has_error():
            print(f'!! error: {profiler.get_err_msg()}')

        print('-- Profiler should run without error')
        self.assertTrue(profiler.has_error() is False)

        # print(f'-- Original dataset has {num_features_orig} features')
        # self.assertEqual(profiler.num_variables, num_features_orig)

        print(f'-- Profile metadata has {num_features_profile} features')
        info = profiler.data_profile
        self.assertTrue('variables' in info)
        num_features_in_profile = len(info['variables'].keys())
        # self.assertEqual(num_features_in_profile, num_features_profile)
        self.assertTrue(num_features_in_profile <= settings.PROFILER_COLUMN_LIMIT)

        # pvars = profiler.profile_variables
        # self.assertTrue('variables' in info)
        # self.assertTrue(len(pvars['variables']) <= settings.PROFILER_COLUMN_LIMIT)
        # self.assertEqual(len(pvars['variables']), info['dataset']['variableCount'])
        self.assertEqual(info['dataset']['variableCount'],
                         len(info['dataset']['variableOrder']))

        print('rows! ->', info['dataset']['rowCount'])

        self.assertTrue(info['dataset']['rowCount'] == num_rows)

        # make the sure the "dataset.variableOrder" column names are in the "variables" dict
        #
        for idx, colname in info['dataset']['variableOrder']:
            self.assertTrue(colname in info['variables'])

    #@skip
    def test_005_profile_good_files(self):
        """(05) Profile several good files"""
        msgt(self.test_005_profile_good_files.__doc__)

        msgt('-- Profile gking-crisis.tab')
        # https://dataverse.harvard.edu/file.xhtml?persistentId=doi:10.7910/DVN/OLD7MB/ZI4N3J&version=4.2
        self.profile_good_file('gking-crisis.tab', 19, 19, 3345)

        msgt('-- Profile voter_validation_lwd.csv')
        # https://github.com/privacytoolsproject/PSI-Service/blob/develop/data/voter_validation_lwd.csv
        self.profile_good_file('voter_validation_lwd.csv', 35, 35, 20771)

        msgt('-- Profile teacher_climate_survey_lwd.csv')
        # https://github.com/privacytoolsproject/PSI-Service/blob/develop/data/teacher_climate_survey_lwd.csv
        self.profile_good_file('teacher_climate_survey_lwd.csv', 132, 132, 1500)

        # Don't save row count
        self.profile_good_file('teacher_climate_survey_lwd.csv', 132, 132, 1500, **dict(save_row_count=False))


    def test_010_profile_good_file(self):
        """(10) Profile file directory"""
        msgt(self.test_010_profile_good_file.__doc__)

        # File to profile
        #
        filepath = join(TEST_DATA_DIR, 'fearonLaitin.csv')
        print('-- filepath is readable', filepath)
        self.assertTrue(isfile(filepath))

        # Retrieve DataSetInfo, save the file to this object
        #
        dsi = DataSetInfo.objects.get(object_id=self.ds_01_object_id)
        self.assertEqual(dsi.depositor_setup_info.user_step,
                         DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED)

        # Run profiler
        #
        profiler = profiler_tasks.run_profile_by_filepath(filepath, dsi.object_id)

        # Shouldn't have errors
        if profiler.has_error():
            print(f'!! error: {profiler.get_err_msg()}')

        print('-- Profiler should run without error')
        self.assertTrue(profiler.has_error() is False)
        print('-- Original dataset has 69 features, default limit should set to first 20')
        self.assertEqual(profiler.num_variables, settings.PROFILER_COLUMN_LIMIT)

        profile_json_str1 = json.dumps(profiler.data_profile, cls=DjangoJSONEncoder, indent=4)

        # Re-retrieve object and data profile
        dsi = DataSetInfo.objects.get(object_id=dsi.object_id)
        info = dsi.data_profile_as_dict()
        print('end step:', dsi.depositor_setup_info.user_step)
        self.assertEqual(dsi.depositor_setup_info.user_step,
                         DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE)

        # print('-- Profiler reads only first 20 features')
        self.assertTrue('variables' in info)
        self.assertEqual(len(info['variables'].keys()), settings.PROFILER_COLUMN_LIMIT)

        print('-- Profiler output is the same as the output saved to the DataSetInfo object')
        profile_json_str2 = json.dumps(info, cls=DjangoJSONEncoder, indent=4)
        self.assertTrue(profile_json_str1, profile_json_str2)
        print(profile_json_str2)

        # self.assertEqual(dsi.profile_variables['dataset']['variableCount'],
        #                  settings.PROFILER_COLUMN_LIMIT)

        self.assertEqual(dsi.profile_variables['dataset']['variableCount'],
                         len(dsi.profile_variables['dataset']['variableOrder']))

        # make the sure the "dataset.variableOrder" column names are in the "variables" dict
        #
        for idx, colname in dsi.profile_variables['dataset']['variableOrder']:
            self.assertTrue(colname in dsi.profile_variables['variables'])

    def test_020_bad_files(self):
        """(20) Test bad file type"""
        msgt(self.test_020_bad_files.__doc__)

        # Bad file: image file
        #
        print('-- Try to profile an image file')
        filepath = join(TEST_DATA_DIR, 'image_file.png')
        self.assertTrue(isfile(filepath))

        with self.assertRaises(UnicodeDecodeError):
            profiler = profiler_tasks.run_profile_by_filepath(filepath)

        # print(f'!! error: {profiler.get_err_msg()}')
        # self.assertTrue(profiler.has_error())
        # error_msg = profiler.get_err_msg()
        # self.assertTrue(profiler.get_err_msg().find(ProfileHandler.ERR_FAILED_TO_READ_DATASET) > -1)
        # self.assertTrue(error_msg.find('UnicodeDecodeError') > -1 or
        #                 error_msg.find('ParserError') > -1)

        # Bad file: empty file
        #
        print('-- Try to profile an empty file')
        filepath = join(TEST_DATA_DIR, 'empty_file.csv')
        self.assertTrue(isfile(filepath))

        with self.assertRaises(DelimiterNotFoundException):
            profiler = profiler_tasks.run_profile_by_filepath(filepath)

        # print(f'!! error: {profiler.get_err_msg()}')
        # self.assertTrue(profiler.has_error())
        # self.assertTrue(profiler.get_err_msg().find(ProfileHandler.ERR_FAILED_TO_READ_DATASET) > -1)
        # self.assertTrue(profiler.get_err_msg().find('EmptyDataError') > -1)

    def test_30_filefield_empty(self):
        """(30) Test with empty file field"""
        msgt(self.test_30_filefield_empty.__doc__)

        # Retrieve DataSetInfo
        #
        dsi = DataSetInfo.objects.get(object_id=self.ds_01_object_id)
        self.assertEqual(dsi.depositor_setup_info.user_step, \
                         DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED)

        # Try to profile and empty Django FileField
        with self.assertRaises(ValueError):
            profiler = profiler_tasks.run_profile_by_filefield(dsi.object_id)

        # Error!
        # print(profiler.get_err_msg())
        # print('dsi2.depositor_setup_info.user_step', dsi2.depositor_setup_info.user_step)
        # self.assertTrue(profiler.get_err_msg(), ProfileHandler.ERR_DATASET_POINTER_NOT_SET)

        # Retrieve the saved DataSetInfo, the DepositorSetupInfo should have a new status
        dsi2 = DataSetInfo.objects.get(object_id=self.ds_01_object_id)
        self.assertEqual(dsi2.depositor_setup_info.user_step,
                         DepositorSetupInfo.DepositorSteps.STEP_9300_PROFILING_FAILED)

    def test_40_filefield_correct(self):
        """(40) Test using file file with legit file"""
        msgt(self.test_40_filefield_correct.__doc__)

        # Retrieve DataSetInfo
        #
        dsi = DataSetInfo.objects.get(object_id=self.ds_01_object_id)
        self.assertEqual(dsi.depositor_setup_info.user_step, \
                         DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED)

        # Attach the file to the DataSetInfo's file field
        #
        filename = 'fearonLaitin.csv'
        filepath = join(TEST_DATA_DIR, filename)
        self.assertTrue(isfile(filepath))

        django_file = File(open(filepath, 'rb'))

        dsi.source_file.save(filename, django_file)
        dsi.save()

        # Run the profile using the Django file field
        profiler = profiler_tasks.run_profile_by_filefield(dsi.object_id)

        # Should be no error an correct number of features
        self.assertTrue(profiler.has_error() is False)
        self.assertEqual(profiler.num_variables, settings.PROFILER_COLUMN_LIMIT)

        # Re-retrieve DataSetInfo
        #
        dsi2 = DataSetInfo.objects.get(object_id=self.ds_01_object_id)

        info = dsi2.data_profile_as_dict()

        # print('-- Profiler reads only first 20 features')
        self.assertTrue('variables' in info)
        # self.assertEqual(len(info['variables'].keys()), settings.PROFILER_COLUMN_LIMIT)

        self.assertEqual(dsi2.depositor_setup_info.user_step, \
                         DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE)

        #print('dsi2.profile_variables', dsi2.profile_variables)
        # self.assertEqual(len(dsi2.profile_variables['variables'].keys()),
        #                  settings.PROFILER_COLUMN_LIMIT)

        # self.assertEqual(dsi2.profile_variables['dataset']['variableCount'],
        #                  settings.PROFILER_COLUMN_LIMIT)

        self.assertEqual(dsi2.profile_variables['dataset']['variableCount'],
                         len(dsi2.profile_variables['dataset']['variableOrder']))

        # make the sure the "dataset.variableOrder" column names are in the "variables" dict
        #
        for idx, colname in dsi2.profile_variables['dataset']['variableOrder']:
            self.assertTrue(colname in dsi2.profile_variables['variables'])


    def test_050_bad_column_limit(self):
        """(50) Profile bad column limit"""
        msgt(self.test_050_bad_column_limit.__doc__)

        # File to profile
        #
        filepath = join(TEST_DATA_DIR, 'fearonLaitin.csv')
        print('-- filepath is readable', filepath)
        self.assertTrue(isfile(filepath))

        # Run profiler
        #
        params = {pstatic.KW_MAX_NUM_FEATURES: -1}

        self.assertRaises(ColumnLimitLessThanOne,
                          profiler_tasks.run_profile_by_filepath,
                          filepath, None, **params)
