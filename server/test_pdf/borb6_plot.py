
from decimal import Decimal
import random
from borb.pdf.canvas.layout.image.barcode import Barcode, BarcodeType
from borb.pdf.canvas.layout.image.chart import Chart
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from borb.pdf.canvas.layout.text.paragraph import Paragraph

import matplotlib.pyplot as MatPlotLibPlot
import numpy as np
import pandas as pd

from dp_text import get_intro_para


def create_plot() -> None:
    # generate dataset
    df = pd.DataFrame(
        {
            "X": range(1, 101),
            "Y": np.random.randn(100) * 15 + range(1, 101),
            "Z": (np.random.randn(100) * 15 + range(1, 101)) * 2,
        }
    )

    hist_vals = {'categories': list(range(1,13)),
                 'values': [random.randint(1, 100) for x in range(1, 13)]}
    print('hist_vals', hist_vals)
    fig = MatPlotLibPlot.figure()
    ax = fig.add_subplot()
    ax.bar(x=hist_vals['categories'], height=hist_vals['values'])
    ax.set_xlabel('Month')
    ax.set_ylabel('Thunderstorms')
    #ax.view_init(30, 185)

    # orig plot
    """
    fig = MatPlotLibPlot.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(df["X"], df["Y"], df["Z"], c="skyblue", s=60)
    ax.view_init(30, 185)
    """
    # retur
    return MatPlotLibPlot.gcf()

"""
     fig = plt.figure(tight_layout=True, figsize=self.figure_size)
        ax = fig.add_subplot()
        ax.bar(x=statistic['result']['categories'], height=statistic['result']['value'])
        ax.set_xlabel(statistic['variable'])
        filename = '_'.join([statistic['variable'], statistic['statistic']])
        fig.savefig('./images/' + filename + '.png')
"""

def main():
    doc: Document = Document()
    page: Page = Page()
    doc.append_page(page)

    layout: PageLayout = SingleColumnLayout(page)
    layout.add(Paragraph(get_intro_para(), font="Times-roman"))

    layout.add(Chart(create_plot(),
                     width=Decimal(256),
                     height=Decimal(256)))

    #p: Paragraph = Paragraph("Hello World!")

    with open("output.pdf", "wb") as out_file_handle:
        PDF.dumps(out_file_handle, doc)


if __name__ == "__main__":
    main()