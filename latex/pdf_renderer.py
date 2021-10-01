import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import gridspec
from pylatex import Document, Section, Command, Tabular, MultiColumn, Figure, Center
from pylatex.utils import NoEscape
from typing import List, Tuple, Dict

matplotlib.use('Agg')  # Not to use X server.


class PDFRenderer(object):

    def __init__(self, statistics: dict, histograms: dict, figure_width=8):
        """
        :param statistics: List of tuples (name, value)
        :param histograms: List of tuples (name, list[int])
        """
        self.doc = Document('output')
        self.statistics = statistics
        self.histograms = histograms
        self.figure_size = (figure_width, 3 * len(histograms))
        self.fill_document()

    def set_title(self, title):
        self.doc.preamble.append(Command('title', title))
        self.doc.append(NoEscape(r'\maketitle'))

    def add_author(self, author):
        self.doc.preamble.append(Command('author', author))

    def set_date(self):
        self.doc.preamble.append(Command('date', NoEscape(r'\today')))

    def build_statistics_table(self):
        if not self.statistics:
            return
        self.doc.append(Command('centering'))
        with self.doc.create(Section('DP Statistics')):
            table1 = Tabular('|c|c|')
            table1.add_hline()
            table1.add_row((MultiColumn(2, align='|c|', data='Summary'),))
            table1.add_hline()
            for stat, value in self.statistics.items():
                table1.add_row((stat, value))
                table1.add_hline()
            self.doc.append(table1)

    def build_histograms(self):
        if not self.histograms:
            return
        fig = plt.figure(tight_layout=True, figsize=self.figure_size)
        gs = gridspec.GridSpec(len(self.histograms), 2)
        for i, hist_dict in enumerate(self.histograms):
            ax = fig.add_subplot(gs[i, :])
            ax.bar(x=hist_dict['data'], height=hist_dict['height'])
            ax.set_xlabel(hist_dict['name'])
        with self.doc.create(Section('DP Histograms')):
            with self.doc.create(Figure(position='htbp')) as plot:
                plot.add_plot()
                plot.add_caption('DP Histograms')

    def fill_document(self):
        self.build_statistics_table()
        self.build_histograms()

    def save_pdf(self, filepath):
        self.doc.generate_pdf(filepath=filepath, clean_tex=False)

    def save_latex(self, filepath):
        self.doc.generate_tex(filepath=filepath)

    def get_latex(self):
        return self.doc.dumps()


def generate_example_histogram(title, data_size):
    data = range(0, data_size)
    labels = data
    heights = np.random.randint(low=5, high=10, size=data_size)
    return title, {'data': data, 'labels': labels, 'height': heights}


if __name__ == '__main__':

    np.random.seed(19680801)
    number_of_histograms = 2
    data_size = 10

    statistics = [("mean", 3.14159), ("count", 10)]
    histograms = [generate_example_histogram(f'Histogram {i}', data_size) for i in range(0, number_of_histograms)]

    renderer = PDFRenderer(statistics, histograms)
    renderer.set_title("Test Output")
    renderer.add_author("Ethan Cowan")
    renderer.set_date()
    renderer.fill_document()
    renderer.save_pdf('test.pdf')
