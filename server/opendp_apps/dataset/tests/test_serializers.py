from unittest import TestCase

from opendp_apps.analysis.serializers import ReleaseInfoSerializer


class TestReleaseInfoSerializer(TestCase):

    def setUp(self) -> None:
        self.request = {
            "analysis_plan_id": 0,
            "dp_statistics": [{
                 "error": "",
                 "label": "EyeHeight",
                 "locked": False,
                 "epsilon": 0.0625,
                 "variable": "eyeHeight",
                 "statistic": "mean",
                 "fixed_value": "5",
                 "handle_as_fixed": True,
                 "missing_values_handling": "insert_fixed"
                 }]
         }

    def test_save(self):
        serializer = ReleaseInfoSerializer(data=self.request)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})
