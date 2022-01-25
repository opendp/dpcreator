from unittest import TestCase

from pdf_renderer import PDFRenderer


class TestPDFRenderer(TestCase):

    def setUp(self) -> None:
        self.statistics = [
                {
                    "result": {
                        "value": 0.3684799824191177
                    },
                    "variable": "EyeHeight",
                    "statistic": "mean",
                },
                {
                    "name": "test",
                    "data": [1, 2, 3, 4, 5],
                    "height": [1, 2, 3, 4, 5]
                }
            ]

    def test_render(self):
        from mock_data import dp_release
        pdf_renderer = PDFRenderer(dp_release, self.statistics, 4, 4)
        self.assertIsNotNone(pdf_renderer.get_latex())
