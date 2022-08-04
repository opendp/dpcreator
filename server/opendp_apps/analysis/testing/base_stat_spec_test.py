from django.contrib.auth import get_user_model
from django.test import TestCase

from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.dataset.models import DataSetInfo


class StatSpecTestCase(TestCase):

    def setUp(self):
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

    def retrieve_new_plan(self):
        """
        Convenience method to create a new plan
        """

        # Create a plan
        dataset_info = DataSetInfo.objects.get(id=4)
        plan_info = AnalysisPlanUtil.create_plan(dataset_info.object_id, self.user_obj)
        self.assertTrue(plan_info.success)
        orig_plan = plan_info.data

        # Retrieve it
        analysis_plan = AnalysisPlan.objects.first()
        self.assertEqual(orig_plan.object_id, analysis_plan.object_id)

        return analysis_plan
