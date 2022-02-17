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
from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.layout.image.barcode import Barcode, BarcodeType
from borb.pdf.canvas.layout.image.chart import Chart
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.canvas.line_art.line_art_factory import LineArtFactory
#from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.table.flexible_column_width_table import FlexibleColumnWidthTable
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
     OPEN_SANS_ITALIC,
     DPCREATOR_LOGO_PATH)

class PDFReportMaker(BasicErrCheck):

    # basic_font = 'Times-roman'


    def __init__(self, release_dict=None):
        """Init w/...."""
        self.release_dict = release_dict
        if not release_dict:
            self.release_dict = self.get_test_release()

        self.basic_font = get_custom_font(OPEN_SANS_LIGHT)
        self.basic_font_italic = get_custom_font(OPEN_SANS_ITALIC)
        self.basic_font_size = Decimal(10)
        self.tbl_font_size = Decimal(9)
        self.tbl_border_color = HexColor("#cbcbcb")

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

    def get_tbl_cell_ital(self, content, col_span=1, padding=0):
        """Get table cell, putting the content in italics"""
        return self._get_tbl_cell(content,
                                 self.basic_font_italic,
                                 self.tbl_font_size,
                                 Alignment.LEFT,
                                 col_span=col_span,
                                 padding_left=padding)

    def get_tbl_cell_lft_pad(self, content, padding=10):
        return self._get_tbl_cell(content,
                                  self.basic_font,
                                  self.tbl_font_size,
                                  Alignment.LEFT,
                                  col_span=1,
                                  padding_left=padding)

    def get_tbl_cell_align_rt(self, content):
        return self._get_tbl_cell(content, self.basic_font, self.tbl_font_size, Alignment.RIGHT)

    def _get_tbl_cell(self, content, font=None, font_size=None, text_alignment=None, col_span=1, padding_left=0) -> TableCell:
        """Return a Paragraph within a TableCell"""
        if not font:
            font = self.basic_font
        if not font_size:
            font = self.basic_font_size
        if not text_alignment:
            text_alignment = Alignment.LEFT

        p = Paragraph(content,
                      font=font,
                      font_size=font_size,
                      padding_left=Decimal(padding_left),
                      text_alignment=text_alignment)
        return TableCell(p,
                         border_color=self.tbl_border_color,
                         col_span=col_span)


    def create_pdf(self):
        """Start making the PDF"""
        doc: Document = Document()
        page = Page(PageSize.LETTER_PORTRAIT.value[0], PageSize.LETTER_PORTRAIT.value[1])

        doc.append_page(page)

        self.layout: PageLayout = SingleColumnLayout(page)

        #self.layout.add(Image(DPCREATOR_LOGO_PATH,
        #    width=Decimal(144), height=64))

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

                subtitle = f"{stat_cnt}. Variable: {stat_info['variable']}; Statistic: Differentially Private {stat_info['statistic']}"

                self.layout.add(Paragraph(subtitle,
                                          font=get_custom_font(OPEN_SANS_SEMI_BOLD),
                                          font_size=self.basic_font_size,
                                          multiplied_leading=Decimal(1.75)))

                self.layout.add(Paragraph(stat_info['description']['text'],
                                          font=self.basic_font,
                                          font_size=self.basic_font_size,
                                          multiplied_leading=Decimal(1.75)))
                # --------------------------------------
                # Create table for parameters
                # --------------------------------------
                tbl_font_size = self.basic_font_size - 1

                table_001 = FlexibleColumnWidthTable(number_of_rows=11,
                                                    number_of_columns=2,
                                                     padding_left=Decimal(20),
                                                    #border_color=self.tbl_border_color
                                                     )

                table_001.add(self.get_tbl_cell_ital("Privacy Parameters", col_span=2))

                table_001.add(self.get_tbl_cell_lft_pad("Epsilon", padding=20))
                table_001.add(self.get_tbl_cell_align_rt(f"{stat_info['epsilon']}"))

                table_001.add(self.get_tbl_cell_lft_pad("Delta", padding=20))
                table_001.add(self.get_tbl_cell_align_rt(f"{stat_info['delta']}"))

                table_001.add(self.get_tbl_cell_ital("Metadata Parameters", col_span=2))

                table_001.add(self.get_tbl_cell_ital("Bounds", col_span=2, padding=20))

                table_001.add(self.get_tbl_cell_lft_pad("Min", padding=40))
                table_001.add(self.get_tbl_cell_align_rt(f"{stat_info['bounds']['min']}"))

                table_001.add(self.get_tbl_cell_lft_pad("Max", padding=40))
                table_001.add(self.get_tbl_cell_align_rt(f"{stat_info['bounds']['max']}"))

                table_001.add(self.get_tbl_cell_lft_pad("Confidence Level", padding=20))
                table_001.add(self.get_tbl_cell_align_rt(f"{stat_info['confidence_level']}"))

                # Missing Value Handling
                table_001.add(self.get_tbl_cell_ital("Missing Value Handling", col_span=2))

                table_001.add(self.get_tbl_cell_lft_pad("Type", padding=20))
                missing_val_handling = stat_info['missing_value_handling']['type']
                print('>>> missing_val_handling', missing_val_handling)
                if missing_val_handling == astatic.MISSING_VAL_INSERT_FIXED:
                    table_001.add(self.get_tbl_cell_lft_pad(\
                        astatic.missing_val_label(astatic.MISSING_VAL_INSERT_FIXED)))

                    table_001.add(self.get_tbl_cell_lft_pad("Value", padding=20))
                    table_001.add(self.get_tbl_cell_align_rt(\
                        f"{stat_info['missing_value_handling']['fixed_value']}"))

                table_001.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))

                #table_001.no_borders()
                table_001.set_borders_on_all_cells(True, False, True, False) # top, right, left, bottom
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

        line_height = 16

        # Line
        print('ps[0]', ps[0], ps[1])
        # Add logo at the top
        #
        logo_height = 32 # 64 / 2
        logo_width = 72 # 144 / 2
        rect_logo: Rectangle = Rectangle(Decimal(10), ps[1] - line_height - logo_height - Decimal(10),
                                 Decimal(logo_width), Decimal(logo_height))
        Image(
            DPCREATOR_LOGO_PATH,
            width=Decimal(logo_width),
            height=Decimal(logo_height),
        ).layout(page, rect_logo)


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
