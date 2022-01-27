from unittest import TestCase

from mock_data import dp_release, statistics
from pdf_renderer import PDFRenderer


class TestPDFRenderer(TestCase):

    def setUp(self) -> None:
        self.pdf_renderer = PDFRenderer(dp_release, statistics, 4, 4)

    def test_render(self):
        self.assertIsNotNone(self.pdf_renderer.get_latex())

    def test_parameter_formatter(self):
        formatted_parameters = self.pdf_renderer.parameter_formatter(statistics[0])
        self.assertEqual('Epsilon: 1.0	Delta: 0.0 	CL: 0.95	Accuracy: 8.987196833391316 	'
                         'Missing value type: insert_fixed 	Missing value: 4', formatted_parameters)


