"""
Create a PDF report based on a DP Release
"""
import os, sys
from os.path import abspath, dirname, isdir, join
import dateutil

CURRENT_DIR = dirname(abspath(__file__))

from django.template.loader import render_to_string

from decimal import Decimal
import json

import random
import typing
from borb.pdf.canvas.layout.image.barcode import Barcode, BarcodeType
from borb.pdf.canvas.layout.image.chart import Chart
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.canvas.line_art.line_art_factory import LineArtFactory
#from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.table.flexible_column_width_table import FlexibleColumnWidthTable  as Table
from borb.pdf.canvas.layout.table.table import TableCell

from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.page.page_size import PageSize
from borb.pdf.pdf import PDF
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.line_art.line_art_factory import LineArtFactory
from borb.pdf.canvas.geometry.rectangle import Rectangle
from borb.pdf.canvas.layout.shape.shape import Shape
from borb.pdf.canvas.color.color import HSVColor, HexColor, Color

import matplotlib.pyplot as MatPlotLibPlot
import numpy as np
import pandas as pd

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.dp_reports.font_util import \
    (get_custom_font,
     OPEN_SANS_LIGHT,
     OPEN_SANS_REGULAR,
     OPEN_SANS_SEMI_BOLD,
     OPEN_SANS_BOLD,
     OPEN_SANS_ITALIC)

class PDFReportMaker(BasicErrCheck):

    # basic_font = 'Times-roman'


    def __init__(self, release_dict=None):
        """Init w/...."""
        self.release_dict = release_dict
        if not release_dict:
            self.release_dict = self.get_test_release()

        self.basic_font = get_custom_font(OPEN_SANS_LIGHT)
        self.basic_font_size = Decimal(10)

        self.layout = None
        self.creation_date = None

        self.format_release()

        self.create_pdf()

    def format_release(self):
        """Update release values"""
        self.creation_date = dateutil.parser.parse(self.release_dict['created']['iso'])
        self.release_dict['creation_date'] = self.creation_date

    def get_test_release(self):
        """for building"""
        test_release_name = join(CURRENT_DIR, 'test_data', 'sample_release_01.json')
        return json.loads(open(test_release_name, 'r').read())


    def get_centered_para(self, s):
        """Add a paragrah to the layout"""
        p = Paragraph(s,
                      font=get_custom_font(OPEN_SANS_SEMI_BOLD),
                      font_size=Decimal(10),
                      font_color=HexColor('#666666'),
                      multiplied_leading=Decimal(1.25),
                      respect_newlines_in_text=True,
                      text_alignment=Alignment.CENTERED)
        return p

    def create_pdf(self):
        """Start making the PDF"""
        doc: Document = Document()
        page = Page(PageSize.LETTER_PORTRAIT.value[0], PageSize.LETTER_PORTRAIT.value[1])

        doc.append_page(page)

        self.layout: PageLayout = SingleColumnLayout(page)

        # Add line at the top
        #
        self.add_colored_artwork_bottom_right_corner(page)

        # Add title text
        #
        title_text = render_to_string('pdf_report/10_title.txt', self.release_dict)
        self.layout.add(self.get_centered_para(title_text))

        # Add intro text
        #
        intro_text = render_to_string('pdf_report/intro_text.txt', self.release_dict)
        self.layout.add(Paragraph(intro_text,
                                  font=self.basic_font,
                                  font_size=self.basic_font_size,
                                  multiplied_leading=Decimal(1.75)))

        stat_cnt = 0
        for stat_info in self.release_dict['statistics']:
            stat_cnt += 1
            if stat_info['statistic'] == astatic.DP_MEAN:
                subtitle = f"{stat_cnt}. {stat_info['variable']} - {stat_info['statistic']}"
                self.layout.add(Paragraph(subtitle,
                                          font=get_custom_font(OPEN_SANS_SEMI_BOLD),
                                          font_size=self.basic_font_size,
                                          multiplied_leading=Decimal(1.75)))

                tbl_font_size = self.basic_font_size - 1
                table_001 = Table(number_of_rows=8, number_of_columns=2)
                table_001.add(TableCell(Paragraph("Privacy Parameters",
                                                  font=get_custom_font(OPEN_SANS_ITALIC),
                                                  font_size=tbl_font_size,
                                                  ), col_span=2))

                table_001.add(Paragraph("Epsilon",
                                        font=self.basic_font,
                                        font_size=tbl_font_size,
                                        padding_left=Decimal(10),
                                        ))
                table_001.add(Paragraph(f"{stat_info['epsilon']}",
                                        font=self.basic_font,
                                        font_size=tbl_font_size,
                                        text_alignment=Alignment.RIGHT
                                        ))
                table_001.add(Paragraph("Delta",
                                        font=self.basic_font,
                                        font_size=tbl_font_size,
                                        padding_left=Decimal(10),
                                        ))
                table_001.add(Paragraph(f"{stat_info['delta']}",
                                        font=self.basic_font,
                                        font_size=tbl_font_size,
                                        text_alignment=Alignment.RIGHT
                                        ))

                table_001.add(TableCell(Paragraph("Metadata Parameters",
                                                  font=get_custom_font(OPEN_SANS_ITALIC),
                                                  font_size=tbl_font_size,
                                                  ), col_span=2))

                table_001.add(TableCell(Paragraph("Bounds",
                                                  font=get_custom_font(OPEN_SANS_ITALIC),
                                                  font_size=tbl_font_size,
                                                  padding_left=Decimal(10),
                                                  ), col_span=2))
                table_001.add(Paragraph("Min",
                                        font=self.basic_font,
                                        font_size=tbl_font_size,
                                        padding_left=Decimal(20),
                                        ))
                table_001.add(Paragraph(f"{stat_info['bounds']['min']}",
                                        font=self.basic_font,
                                        font_size=tbl_font_size,
                                        text_alignment=Alignment.RIGHT
                                        ))
                table_001.add(Paragraph("Max",
                                        font=self.basic_font,
                                        font_size=self.basic_font_size,
                                        padding_left=Decimal(20)
                                        ))
                table_001.add(Paragraph(f"{stat_info['bounds']['max']}",
                                        font=self.basic_font,
                                        font_size=self.basic_font_size,
                                        text_alignment=Alignment.RIGHT
                                        ))
                table_001.add(Paragraph("Confidence Level",
                                        font=self.basic_font,
                                        font_size=self.basic_font_size,
                                        padding_left=Decimal(10)
                                        ))
                table_001.add(Paragraph(f"{stat_info['confidence_level']}",
                                        font=self.basic_font,
                                        font_size=self.basic_font_size,
                                        text_alignment=Alignment.RIGHT
                                        ))

                table_001.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))

                #table_001.no_borders()
                self.layout.add(table_001)

                # Add test plot
        #
        self.layout.add(Chart(self.create_plot(),
                         width=Decimal(256),
                         height=Decimal(256)))

        # p: Paragraph = Paragraph("Hello World!")

        fname = join(CURRENT_DIR, 'test_data', 'pdf_report_01.pdf')
        with open(fname, "wb") as out_file_handle:
            PDF.dumps(out_file_handle, doc)
        print(f'PDF created: {fname}')
        os.system(f'open {fname}')


    def create_plot(self):

        hist_vals = {'categories': list(range(1,13)),
                     'values': [random.randint(1, 100) for x in range(1, 13)]}
        print('hist_vals', hist_vals)
        fig = MatPlotLibPlot.figure()
        ax = fig.add_subplot()
        ax.bar(x=hist_vals['categories'], height=hist_vals['values'])
        ax.set_xlabel('Month')
        ax.set_ylabel('Thunderstorms')

        # orig plot
        """
        fig = MatPlotLibPlot.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(df["X"], df["Y"], df["Z"], c="skyblue", s=60)
        ax.view_init(30, 185)
        """
        # return the current figure
        return MatPlotLibPlot.gcf()


    def add_colored_artwork_bottom_right_corner(self, page: Page) -> None:
        """
        This method will add a blue/purple artwork of lines
        and squares to the bottom right corner
        of the given Page
        """
        ps: typing.Tuple[Decimal, Decimal] = PageSize.LETTER_PORTRAIT.value

        # Line
        print('ps[0]', ps[0], ps[1])

        line_height = 16
        # lower_left_x, lower_left_y, width, height
        r: Rectangle = Rectangle(Decimal(0), ps[1] - line_height, ps[0], Decimal(line_height))
        Shape(
            points=LineArtFactory.rectangle(r),
            stroke_color=HexColor("#a41d30"),
            fill_color=HexColor("#a41d30"),
        ).layout(page, r)

        line_height2 = 2
        r: Rectangle = Rectangle(Decimal(0),
                                 ps[1] - line_height - line_height2,
                                 ps[0], Decimal(line_height2))
        Shape(
            points=LineArtFactory.rectangle(r),
            stroke_color=HexColor("#666666"),
            fill_color=HexColor("#666666"),
        ).layout(page, r)

        return

        # Square
        Shape(
            points=[
                (ps[0] - 64, 40),
                (ps[0] - 32, 40),
                (ps[0] - 32, 40 + 32),
                (ps[0] - 64, 40 + 32),
            ],
            stroke_color=HexColor("#eb3f79"),
            fill_color=HexColor("#eb3f79"),
        ).layout(page, Rectangle(ps[0] - 64, 40, 32, 32))

        return

        # Square
        Shape(
            points=[
                (ps[0] - 32, 40),
                (ps[0], 40),
                (ps[0], 40 + 32),
                (ps[0] - 32, 40 + 32),
            ],
            stroke_color=HexColor("d53067"),
            fill_color=HexColor("d53067"),
        ).layout(page, Rectangle(ps[0] - 32, 40, 32, 32))

        # Square
        Shape(
            points=[
                (ps[0] - 64, 40),
                (ps[0] - 32, 40),
                (ps[0] - 32, 40 + 32),
                (ps[0] - 64, 40 + 32),
            ],
            stroke_color=HexColor("eb3f79"),
            fill_color=HexColor("eb3f79"),
        ).layout(page, Rectangle(ps[0] - 64, 40, 32, 32))

        # Triangle
        Shape(
            points=[
                (ps[0] - 96, 40),
                (ps[0] - 64, 40),
                (ps[0] - 64, 40 + 32),
            ],
            stroke_color=HexColor("e01b84"),
            fill_color=HexColor("e01b84"),
        ).layout(page, Rectangle(ps[0] - 96, 40, 32, 32))
