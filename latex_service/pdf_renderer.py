import matplotlib
import matplotlib.pyplot as plt

from pylatex import Document, Section, Command, Tabular, Figure, LineBreak
from pylatex.basic import NewPage
from pylatex.utils import NoEscape
from typing import List, Dict

matplotlib.use('Agg')  # Not to use X server.


class PDFRenderer(object):

    def __init__(self, dp_release: Dict, statistics: List, figure_width=4, figure_height=3):
        """
        Entry point for creating latex source and building PDFs based on input data.
        :param dp_release: Dict of data points related to the computation
        :param statistics: Dict
        """
        self.doc = Document('output', geometry_options={'margin': "2cm"})
        self.dp_release = dp_release
        self.title = dp_release['name']
        self.created = dp_release['created']['human_readable']
        self.statistics = statistics
        self.figure_size = (figure_width, figure_height)

    def set_title(self):
        """
        Add a title for the document in latex
        :return:
        """
        self.doc.preamble.append(Command('title', 'Replication Data for: ' + self.title))
        self.doc.append(NoEscape(r'\maketitle'))

    def add_author(self, author):
        """
        Insert an author's name
        :param author:
        :return:
        """
        self.doc.preamble.append(Command('author', author))

    def parameter_formatter(self, statistic):
        """
        This block refers to the row that contains the parameters used to calculate a result
        :param statistic:
        :return:
        """
        return '\t'.join([
            f'Epsilon: {statistic["epsilon"]}', f'Delta: {statistic["delta"]} ',
            f'CL: {statistic["confidence_level"]}', f'Accuracy: {statistic["accuracy"]["value"]} ',
            f'Missing value type: {statistic["missing_value_handling"]["type"]} ',
            f'Missing value: {statistic["missing_value_handling"]["fixed_value"]}'
        ])

    def build_header(self):
        """
        Build the header for the document, including the title
        :return:
        """
        self.set_title()
        self.doc.append("Replication Data for: " + self.title)
        self.doc.append(LineBreak())
        self.doc.append(LineBreak())
        self.doc.append("Created: " + self.created)
        self.doc.append(LineBreak())
        self.doc.append(LineBreak())
        self.doc.append('Dataverse url: tbd')

    def _build_row(self, statistic):
        """
        Add a single row of results. Works for both single values and histograms.
        :param statistic:
        :return:
        """
        result_table = Tabular('p{2cm}p{4cm}p{2cm}p{8cm}', row_height=3)
        result_table.add_row((statistic['statistic'], statistic['variable'], statistic['result']['value'],
                              statistic['accuracy']['message']))
        self.doc.append(result_table)
        self.doc.append(LineBreak())
        param_table = Tabular('p{2cm}p{9cm}p{9cm}')
        param_table.add_row(('Parameters: ', self.parameter_formatter(statistic), ''))
        self.doc.append(param_table)
        self.doc.append(LineBreak())

    def _build_histogram(self, statistic):
        """
        Insert a histogram figure into the document
        :param statistic:
        :return:
        """
        fig = plt.figure(tight_layout=True, figsize=self.figure_size)
        ax = fig.add_subplot()
        ax.bar(x=statistic['result']['categories'], height=statistic['result']['value'])
        ax.set_xlabel(statistic['variable'])
        with self.doc.create(Figure(position='htbp')) as plot:
            plot.add_plot()

    def build_statistics_table(self):
        """
        Iterate over all of the given statistics, adding rows and images based on the
        statistic type
        :return:
        """
        if not self.statistics:
            return
        self.doc.append(Command('centering'))
        with self.doc.create(Section('Statistics')):
            header_table = Tabular('p{2cm}p{4cm}p{2cm}p{8cm}', row_height=3)
            header_table.add_row(('Statistic', 'Variable', 'Result', 'Confidence Level',))
            header_table.add_hline()
            self.doc.append(header_table)
            self.doc.append(LineBreak())
            single_value_stats = [x for x in self.statistics if x['statistic'] != 'histogram']
            histograms = [x for x in self.statistics if x['statistic'] == 'histogram']
            for statistic in single_value_stats:
                self._build_row(statistic)
            for histogram in histograms:
                self.doc.append(NewPage())
                self._build_row(histogram)
                self._build_histogram(histogram)

    def fill_document(self):
        """
        Create all of the latex for the file
        :return:
        """

        self.build_header()
        self.build_statistics_table()

    def save_pdf(self, filepath):
        """
        Render the document to PDF
        :param filepath:
        :return:
        """
        self.doc.generate_pdf(filepath=filepath, clean_tex=False)

    def save_latex(self, filepath):
        """
        Save the latex source
        :param filepath:
        :return:
        """

        self.doc.generate_tex(filepath=filepath)

    def get_latex(self):
        """
        Return the document latex as a string
        :return:
        """

        return self.doc.dumps()


if __name__ == '__main__':
    from mock_data import dp_release, statistics, generate_example_histogram

    variable_template = "SomeVariable"
    number_of_histograms = 4
    for i in range(0, number_of_histograms):
        statistics.append(generate_example_histogram(''.join([variable_template, str(i)]), 4))

    renderer = PDFRenderer(dp_release, statistics)
    renderer.fill_document()
    renderer.save_pdf('test')
