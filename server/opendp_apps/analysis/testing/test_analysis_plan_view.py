from django.contrib.auth import get_user_model

from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest


class TestAnalysisPlanView(BaseEndpointTest):
    fixtures = ['test_data_001.json', 'test_analysis_001.json']
    maxDiff = None

    def setUp(self):
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')
        self.test_file_name = 'Fatigue_data.tab'
        self.client.force_login(self.user_obj)

    def test_delete_without_release_info(self):
        analysis_plan = AnalysisPlan.objects.create(
            analyst=self.user_obj,
            name='Test AnalysisPlan',
            dataset=DataSetInfo.objects.first(),
            user_step='step_700'
        )
        response = self.client.delete(f'/api/analyze/{analysis_plan.object_id}/')
        # object_id = response.json()
        self.assertEqual(response.content, b'')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(AnalysisPlan.objects.count(), 0)

    def test_delete_with_release_info(self):
        release_info = ReleaseInfo.objects.create(
            dataset=DataSetInfo.objects.first(),
            epsilon_used=0.0,
            dp_release={}
        )
        analysis_plan = AnalysisPlan.objects.create(
            analyst=self.user_obj,
            release_info=release_info,
            name='Test AnalysisPlan',
            dataset=DataSetInfo.objects.first(),
            user_step='step_700'
        )
        response = self.client.delete(f'/api/analyze/{analysis_plan.object_id}/')
        self.assertEqual(response.content, b'')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(AnalysisPlan.objects.count(), 0)
