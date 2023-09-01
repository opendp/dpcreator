from os.path import abspath, dirname, join

from django.contrib.auth import get_user_model
from django.core.files import File as DjangoFileObject
from django.test import TestCase
from rest_framework.test import APIClient

from opendp_apps.dataset.models import DatasetInfo
from opendp_apps.utils import datetime_util

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')


class BaseAnalysisPlanTest(TestCase):
    fixtures = ['test_analysis_002.json']

    def setUp(self):
        """Create user object and define file to upload"""

        self.API_ANALYSIS_PREFIX = '/api/analysis-plan/'
        self.API_ANALYSIS_LIST_VIEW_PREFIX = '/api/analysis-plan-list-view/'

        # Create a OpenDP User object
        #
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dp_depositor')
        self.analyst_user_obj, _created = get_user_model().objects.get_or_create(username='dp_analyst')
        self.another_user, _created = get_user_model().objects.get_or_create(username='another_user')

        self.client = APIClient()
        self.client.force_login(self.user_obj)

        self.expiration_date_str = datetime_util.get_expiration_date_str()

        # Define a file to upload
        self.test_file_name = join('teacher_survey', 'teacher_survey.csv')
        self.upload_name = 'Teacher Survey'
        test_file = join(TEST_DATA_DIR, self.test_file_name)

        # Attach the file to the DatasetInfo object and
        #   make sure to start with epsilon = 1.0
        self.dataset_info = DatasetInfo.objects.get(id=2)
        self.dataset_info.source_file.save(self.upload_name, DjangoFileObject(open(test_file, 'rb')))
        self.dataset_info.depositor_setup_info.epsilon = 1.0
        self.dataset_info.save()

        self.dataset_object_id = str(self.dataset_info.object_id)

        self.working_plan_info = dict(object_id=self.dataset_object_id,
                                      name='Teacher survey plan',
                                      description='Release DP Statistics for the teacher survey, version 1',
                                      epsilon=0.25,
                                      expiration_date=self.expiration_date_str)
        # print(json.dumps(self.working_plan_info, indent=4))

