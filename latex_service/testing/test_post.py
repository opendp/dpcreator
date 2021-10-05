import json
import requests

from unittest import TestCase

from app import app


class TestPost(TestCase):

    def setUp(self) -> None:
        self.request = {
            "statistics": [
                {
                    "statistic": "mean",
                    "result": {
                        "value": 3.14
                    }
                }
            ],
            "histograms": [
                {
                    "name": "test",
                    "data": [
                        1, 2, 3, 4, 5
                    ],
                    "height": [
                        1, 2, 3, 4, 5
                    ]
                }
            ],
            "object_id": 1234,
            "base_filename": "test_file"
        }

    def test_post(self):
        response = app.request('/', method="POST", data=json.dumps(self.request))
        self.assertEqual(json.loads(response['data']), {"key": "output/test_file.pdf", "object_id": 1234})
        status_code = int(response['status'].split(' ')[0])
        self.assertEqual(status_code, 200)

    def test_available(self):
        """
        Make sure the service is available at the address "latex"
        :return:
        """
        response = requests.post('http://latex:1234/', json=self.request)
        self.assertEqual(response.json(), {"key": "output/test_file.pdf", "object_id": 1234})
        self.assertEqual(response.status_code, 200)
