import datetime
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
        self.doc = Document('output', geometry_options={'margin': "3cm"})
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
        self.doc.preamble.append(Command('title', f'Differentially Private Release: '
                                                  f'Replication Data for \"{self.title}\"'))
        self.doc.preamble.append(NoEscape(r'\usepackage{graphicx}'))
        self.doc.preamble.append(NoEscape(r'\graphicspath{ {./images/} }'))
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
            f'Epsilon: {statistic["epsilon"]:.4f}', f'Delta: {statistic["delta"]:.4f} ',
            f'CL: {statistic["confidence_level"]}', f'Accuracy: {statistic["accuracy"]["value"]:.4f} ',
            f'Missing value type: {statistic["missing_value_handling"]["type"]} ',
            f'Missing value: {statistic["missing_value_handling"]["fixed_value"]}'
        ])

    def build_header(self):
        """
        Build the header for the document, including the title
        :return:
        """
        date = datetime.date.today().strftime("%B %d, %Y")
        self.set_title()
        # self.doc.append(f"Dataset: \"Replication Data for: {self.title}\"")
        header_table = Tabular('p{40cm}', row_height=3)
        self.doc.append(header_table)
        self.doc.append(f"This report contains differentially private statistics calculated by a user of the DP Creator"
                        f" application on {date} using the dataset  \"{self.title}\" "
                        f"from the Dataverse repository at http://dataverse.harvard.edu.")
        self.doc.append(LineBreak())
        self.doc.append(LineBreak())
        self.doc.append("Differentially private (DP) statistics have calibrated levels of random noise added to them "
                        "by the DP Creator user to protect the privacy of individuals in a dataset while still being "
                        "of high utility. (Links to explanation, etc.). The accuracy/utility of these statistics "
                        "depends on the parameters used to generate the DP statistics. This result contains both the "
                        "DP statistics as well as the parameters used to create them.", )
        self.doc.append(LineBreak())
        self.doc.append(LineBreak())
        self.doc.append(LineBreak())
        self.doc.append(LineBreak())

    def build_table_of_contents(self):
        header_table = Tabular('p{15cm}', row_height=3)
        header_table.add_hline()
        header_table.append("DP Statistics")
        header_table.add_row(("",))
        header_table.append("The variables and statistics calculated were:")
        header_table.add_row(("",))
        for index, stat in enumerate(self.statistics):
            header_table.add_row((f"{index+1}. {stat['variable']} - {stat['statistic']}",))
        self.doc.append(header_table)

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
        filename = '_'.join([statistic['variable'], statistic['statistic']])
        fig.savefig('./images/' + filename + '.png')

    def build_statistics_table(self):
        self.doc.append(LineBreak())
        self.doc.append(LineBreak())
        for index, stat in enumerate(self.statistics):
            stat_table = Tabular('p{15cm}', row_height=3)
            stat_table.add_hline()
            stat_table.add_row((f"{index+1} {stat['variable']} - {stat['statistic']}", ))
            if stat['statistic'] == 'histogram':
                stat_table.add_row((f"Result: {stat['result']['value']}", ))
                self._build_histogram(stat)
                self.doc.append(LineBreak())
                filename = './images/' + '_'.join([stat['variable'], stat['statistic']])
                self.doc.append(NoEscape(r'\includegraphics{' + filename + '.png}'))
                self.doc.append(LineBreak())
            else:
                stat_table.add_row((f"Result: {stat['result']['value']:.4f}", ))

            stat_table.add_row((f"Parameters: {self.parameter_formatter(stat)}", ))
            # stat_table.add_row((f"Parameters: Epsilon: {stat['epsilon']:.4f}\tDelta: {stat['delta']:.4f}"
            #                     f"\tCL: {stat['confidence_level']}\tAccuracy: {stat['accuracy']['value']:.4f}\t'"
            #                     f"Missing value type: {stat['missing_value_handling']['type']} '"
            #                     f"Missing value: {stat['missing_value_handling']['fixed_value']}'", ))
            # if stat['statistic'] == 'histogram':
            # else:
            #     stat_table.add_row(("", ))
            self.doc.append(stat_table)
            self.doc.append(LineBreak())

    def fill_document(self):
        """
        Create all of the latex for the file
        :return:
        """

        self.build_header()
        self.build_table_of_contents()
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
