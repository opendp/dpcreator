import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import gridspec
from pylatex import Document, Section, Command, Tabular, MultiColumn, Figure, Center, Tabularx, LineBreak, FlushLeft
from pylatex.utils import NoEscape
from typing import List, Tuple, Dict

matplotlib.use('Agg')  # Not to use X server.


class PDFRenderer(object):

    def __init__(self, dp_release: Dict, statistics: List, histograms: Dict, figure_width=8):
        """
        :param dp_release: Dict of data points related to the computation
        :param statistics: Dict
        :param histograms: Dict
        """
        self.doc = Document('output', geometry_options={'margin': "2cm"})
        self.dp_release = dp_release
        self.title = dp_release['name']
        self.created = dp_release['created']['human_readable']
        self.statistics = statistics
        self.histograms = histograms
        self.figure_size = (figure_width, 3 * len(histograms))

    def set_title(self):
        self.doc.preamble.append(Command('title', 'Replication Data for: ' + self.title))
        self.doc.append(NoEscape(r'\maketitle'))

    def add_author(self, author):
        self.doc.preamble.append(Command('author', author))

    def parameter_formatter(self, statistic):
        return '\t'.join(f'Epsilon: {statistic["epsilon"]} Delta: {statistic["delta"]} '
                         f'CL: {statistic["confidence_level"]} Accuracy: {statistic["accuracy"]["value"]} '
                         f'Missing value type: {statistic["missing_value_handling"]["type"]} '
                         f'Missing value: {statistic["missing_value_handling"]["fixed_value"]}'.split())

    def build_header(self):
        self.set_title()
        self.doc.append("Replication Data for: " + self.title)
        self.doc.append(LineBreak())
        self.doc.append(LineBreak())
        self.doc.append("Created: " + self.created)
        self.doc.append(LineBreak())
        self.doc.append(LineBreak())
        self.doc.append('Dataverse url: tbd')

    def build_statistics_table(self):
        if not self.statistics:
            return
        self.doc.append(Command('centering'))
        with self.doc.create(Section('Statistics')):
            table1 = Tabular('p{2cm}p{4cm}p{2cm}p{8cm}', row_height=3)
            table1.add_row(('Statistic', 'Variable', 'Result', 'Confidence Level',))
            table1.add_hline()
            for statistic in self.statistics:
                table1.add_row((statistic['statistic'], statistic['variable'], statistic['result']['value'],
                                statistic['accuracy']['message']))
                self.doc.append(table1)
                self.doc.append(LineBreak())
                self.doc.append(LineBreak())
                table2 = Tabular('p{2cm}p{9cm}p{9cm}')
                table2.add_row(('Parameters: ', self.parameter_formatter(statistic), ''))
                self.doc.append(table2)

    def build_histograms(self):
        if not self.histograms:
            return
        fig = plt.figure(tight_layout=True, figsize=self.figure_size)
        gs = gridspec.GridSpec(len(self.histograms), 2)

        for i, hist_dict in enumerate(self.histograms.values()):
            ax = fig.add_subplot(gs[i, :])
            ax.bar(x=hist_dict['data'], height=hist_dict['height'])
            ax.set_xlabel(hist_dict['name'])

        with self.doc.create(Section('DP Histograms')):
            with self.doc.create(Figure(position='htbp')) as plot:
                plot.add_plot()
                plot.add_caption('DP Histograms')

    def fill_document(self):
        self.build_header()
        self.build_statistics_table()
        self.build_histograms()

    def save_pdf(self, filepath):
        self.doc.generate_pdf(filepath=filepath, clean_tex=False)

    def save_latex(self, filepath):
        self.doc.generate_tex(filepath=filepath)

    def get_latex(self):
        return self.doc.dumps()


def generate_example_histograms(title_template, data_size, number_of_histograms):
    result = {}
    for i in range(0, number_of_histograms):
        title = title_template % str(i)
        data = range(0, data_size)
        labels = data
        heights = np.random.randint(low=5, high=10, size=data_size)
        result[title_template] = {'title': title, 'data': data, 'labels': labels,
                                  'height': heights, 'name': 'something random'}
        return result


if __name__ == '__main__':
    np.random.seed(19680801)
    number_of_histograms = 2
    data_size = 10

    dp_release = {"name": "Test Experiment", "created": {"human_readable": "January 04, 2022 at 18:34:53:991957"}}
    statistics = [
        {
            "result": {
                "value": 187
            },
            "epsilon": 1.0,
            "delta": 0.0,
            "accuracy": {
                "value": 8.987196833391316,
                "message": "There is a probability of 95.0% that the DP Count will differ from the true Count by at "
                           "most 8.987196833391316 units. Here the units are the same units the variable "
                           "BlinkFrequency has in the dataset."
            },
            "variable": "BlinkFrequency",
            "statistic": "count",
            "description": {
                "html": "A differentially private <b>Count</b> for variable <b>BlinkFrequency</b> was calculated with "
                        "the result <b>187</b>.  There is a probability of <b>95.0%</b> that the <b>DP Count</b> will "
                        "differ from the true Count by at most <b>8.987196833391316</b> units. Here the units are the "
                        "same units the variable <b>BlinkFrequency</b>} has in the dataset.",
                "text": "A differentially private Count for variable \"BlinkFrequency\" was calculated with the result "
                        "187. There is a probability of 95.0% that the DP Count will differ from the true Count by at "
                        "most 8.987196833391316 units. Here the units are the same units the variable BlinkFrequency "
                        "has in the dataset."
            },
            "confidence_level": 0.95,
            "confidence_level_alpha": 0.05,
            "missing_value_handling": {
                "type": "insert_fixed",
                "fixed_value": "4"
            }
        }
    ]
    histograms = generate_example_histograms(f'Histogram %s', data_size, number_of_histograms)
    renderer = PDFRenderer(dp_release, statistics, histograms)
    renderer.fill_document()
    renderer.save_pdf('test')
