"""
Create a PDF report based on a DP Release
"""
from decimal import Decimal
from decimal import getcontext as get_dec_context
import json

import os
from os.path import abspath, dirname, isfile, join
import dateutil
import random
import typing

CURRENT_DIR = dirname(abspath(__file__))

from django.template.loader import render_to_string

from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.layout.image.barcode import Barcode, BarcodeType
from borb.pdf.canvas.layout.image.chart import Chart
from borb.pdf.canvas.layout.list.unordered_list import UnorderedList
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.canvas.line_art.line_art_factory import LineArtFactory
#from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.table.flexible_column_width_table import FlexibleColumnWidthTable
from borb.pdf.canvas.layout.table.table import TableCell

from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.document import Document
from borb.pdf.page.page import DestinationType
from borb.pdf.page.page import Page
from borb.pdf.page.page_size import PageSize
from borb.pdf.pdf import PDF
from borb.pdf.canvas.layout.text.chunk_of_text import ChunkOfText
from borb.pdf.canvas.layout.text.chunks_of_text import HeterogeneousParagraph
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
    color_crimson = HexColor('#a41d30')
    basic_font = get_custom_font(OPEN_SANS_LIGHT)
    basic_font_italic = get_custom_font(OPEN_SANS_ITALIC)
    basic_font_bold = get_custom_font(OPEN_SANS_SEMI_BOLD)

    def __init__(self, release_dict=None):
        """Init w/...."""
        self.release_dict = release_dict
        if not release_dict:
            self.release_dict = self.get_test_release()
        self.release_json_bytes = bytes(json.dumps(self.release_dict, indent=4), encoding="latin1")

        self.basic_font_size = Decimal(9)
        self.tbl_font_size = Decimal(9)
        self.tbl_border_color = HexColor("#cbcbcb")

        self.pdf_output_file = join(CURRENT_DIR,
                                    'test_data',
                                    'pdf_report_01_%s.pdf' % (self.random_with_N_digits(6)))

        self.layout = None
        self.creation_date = None

        self.format_release()

        self.create_pdf()

    def random_with_N_digits(self, n):
        range_start = 10 ** (n - 1)
        range_end = (10 ** n) - 1
        return random.randint(range_start, range_end)


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
                      font_color=self.color_crimson,
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
                         # border_color=self.tbl_border_color,
                         col_span=col_span)

    def txt_reg(self, val):
        """Return a chunk of text with a regular font"""
        return ChunkOfText(val, font=self.basic_font, font_size=self.basic_font_size)

    def txt_reg_para(self, val):
        """Return a chunk of text with a regular font"""
        return Paragraph(val, font=self.basic_font, font_size=self.basic_font_size)

    def txt_list_para(self, val, padding_left=Decimal(40)):
        """Return a chunk of text with a regular font"""
        return Paragraph(val,
                         # font=self.basic_font,
                         font=get_custom_font(OPEN_SANS_SEMI_BOLD),
                         font_size=self.basic_font_size,
                         font_color=self.color_crimson,
                         padding_left=padding_left,
                         padding_bottom=Decimal(0),
                         padding_top=Decimal(0),
                         margin_top=Decimal(0),
                         margin_bottom=Decimal(0),
                         multiplied_leading=Decimal(.5),
                         )

    def txt_bld(self, val):
        """Return a chunk of text with a bold font"""
        return ChunkOfText(val, font=self.basic_font_bold, font_size=self.basic_font_size)

    def txt_bld_para(self, val):
        """Return a chunk of text with a bold font"""
        return Paragraph(val, font=self.basic_font_bold, font_size=self.basic_font_size)

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

        self.layout.add(Paragraph(('Please read the report carefully, especially in'
                                   'regard to usage of these statistics.'),
                                  font=self.basic_font,
                                  font_size=self.basic_font_size,
                                  multiplied_leading=Decimal(1.75)))

        self.layout.add(Paragraph(('Contents'),
                                  font=get_custom_font(OPEN_SANS_SEMI_BOLD),
                                  font_size=self.basic_font_size,
                                  multiplied_leading=Decimal(1.75)))

        self.layout.add(self.txt_list_para('1. Statistics'))
        stat_cnt = 0
        for stat_info in self.release_dict['statistics']:
            stat_cnt += 1
            stat_type = stat_info['statistic']
            var_name = stat_info['variable']
            self.layout.add(self.txt_list_para(f'1.{stat_cnt}. {var_name} - {stat_type}', 60))

        self.layout.add(self.txt_list_para('2. Data source'))
        self.layout.add(self.txt_list_para('3. OpenDP Library / Usage'))
        self.layout.add(self.txt_list_para('4. Parameter Definitions'))

        stat_cnt = 0
        for stat_info in self.release_dict['statistics']:
            stat_cnt += 1
            stat_type = stat_info['statistic']
            var_name = stat_info['variable']

            subtitle = f"1.{stat_cnt}. {var_name} - " + stat_type.title()
            self.layout.add(Paragraph(subtitle,
                                      font=get_custom_font(OPEN_SANS_SEMI_BOLD),
                                      font_size=self.basic_font_size + Decimal(1),
                                      font_color=self.color_crimson,
                                      multiplied_leading=Decimal(1.75)))

            text_chunks_01 = [
                self.txt_bld(f'Result.'),
                self.txt_reg(f' A '),
                self.txt_bld(f'differentially private (DP) {stat_type}'),
                self.txt_reg(' has been calculated for the variable'),
                self.txt_bld(f" {var_name}."),
                self.txt_reg(' The result,'),
                self.txt_reg(' accuracy measures,'),
                self.txt_reg(' and parameters used to create the statistic are shown below:'),
            ]

            self.layout.add(HeterogeneousParagraph(text_chunks_01,
                                                   padding_left=Decimal(10)))

            if stat_info['statistic'] == astatic.DP_MEAN:


                # -------------------------------------
                # Result table
                # -------------------------------------

                tbl_result = FlexibleColumnWidthTable(number_of_rows=4,
                                                      number_of_columns=2,
                                                      padding_left=Decimal(40),
                                                      padding_right=Decimal(40),
                                                      padding_bottom=Decimal(20),
                                                      )

                tbl_result.add(self.get_tbl_cell_lft_pad("DP Mean", padding=0))
                res_fmt = round(stat_info['result']['value'], 4)
                tbl_result.add(self.get_tbl_cell_align_rt(f"{res_fmt}"))

                tbl_result.add(self.get_tbl_cell_lft_pad("Accuracy", padding=0))
                acc_fmt = round(stat_info['accuracy']['value'], 4)
                tbl_result.add(self.get_tbl_cell_align_rt(f"{acc_fmt}"))

                clevel = round(stat_info['confidence_level'] * 100.0, 1)

                tbl_result.add(self.get_tbl_cell_lft_pad("Confidence Level", padding=0))
                tbl_result.add(self.get_tbl_cell_align_rt(f"{clevel}%"))

                tbl_result.add(self.get_tbl_cell_lft_pad("Description", padding=0))


                acc_desc = (f'There is a probability of {clevel}% that the DP {stat_type.title()} '
                            f' will differ'
                            f' from the true {stat_type.title()} by at most {acc_fmt} units.'
                            f' The units are the same units the variable {var_name} has in the dataset.')

                tbl_result.add(self.get_tbl_cell_lft_pad(acc_desc))


                tbl_result.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))
                tbl_result.set_border_color_on_all_cells(self.color_crimson)
                tbl_result.set_borders_on_all_cells(True, False, True, False) # top, right, left, bottom
                self.layout.add(tbl_result)


                #self.layout.add(Paragraph(stat_info['description']['text'],
                #                          font=self.basic_font,
                #                          font_size=self.basic_font_size,
                #                          multiplied_leading=Decimal(1.75)))

                text_chunks_02 = [
                    self.txt_bld(f'Parameters.'),
                    self.txt_reg(f' The table below shows the parameters used when calculating the DP Mean. For reference, '),
                    self.txt_reg(' a description of each'),
                    self.txt_reg(' parameter may be found at the end of the document.'),
                ]

                self.layout.add(HeterogeneousParagraph(text_chunks_02,
                                                       padding_left=Decimal(10)))

                # self.layout.add(self.txt_bld_para(f'Parameters.'))
                # self.layout.add(self.txt_reg_para(' The table below shows the parameters used when calculating the DP Mean. For reference, a description of each parameter may be found at the end of the document.'))


                # --------------------------------------
                # Create table for parameters
                # --------------------------------------
                table_001 = FlexibleColumnWidthTable(number_of_rows=11,
                                                     number_of_columns=2,
                                                     padding_left=Decimal(40),
                                                     padding_right=Decimal(40),
                                                     border_color=self.color_crimson)


                table_001.add(self.get_tbl_cell_ital("Privacy Parameters", col_span=2))

                table_001.add(self.get_tbl_cell_lft_pad("Epsilon", padding=20))
                table_001.add(self.get_tbl_cell_align_rt(f"{stat_info['epsilon']}"))

                table_001.add(self.get_tbl_cell_lft_pad("Delta", padding=20))
                delta_val = stat_info['delta']
                if delta_val is None:
                    delta_val = '(not applicable)'
                table_001.add(self.get_tbl_cell_align_rt(f'{delta_val}'))

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
                    table_001.add(self.get_tbl_cell_lft_pad(
                        astatic.missing_val_label(astatic.MISSING_VAL_INSERT_FIXED)))

                    table_001.add(self.get_tbl_cell_lft_pad("Value", padding=20))
                    table_001.add(self.get_tbl_cell_align_rt(
                        f"{stat_info['missing_value_handling']['fixed_value']}"))

                table_001.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))

                #table_001.set_border_color_on_all_cells(self.tbl_border_color)
                table_001.set_border_color_on_all_cells(self.color_crimson)
                # table_001.no_borders()
                table_001.set_borders_on_all_cells(True, False, True, False)  # top, right, left, bottom

                # self.layout.add(table_001)

                # Add test plot
        #
        self.layout.add(Chart(self.create_plot(),
                         width=Decimal(256),
                         height=Decimal(256)))

        # Add label for the PDF outline
        #
        doc.add_outline("Differentially Private Release", 0, DestinationType.FIT, page_nr=0)

        # Embed the JSON release in the PDF
        #
        doc.append_embedded_file("release_data.json", self.release_json_bytes)

        with open(self.pdf_output_file, "wb") as out_file_handle:
            PDF.dumps(out_file_handle, doc)
        print(f'PDF created: {self.pdf_output_file}')
        os.system(f'open {self.pdf_output_file}')

    def get_pdf_contents(self):
        """Return the PDF contents"""
        if self.has_error():
            return False, self.get_err_msg()

        if not isfile(self.pdf_output_file):
            return False, f'Not a file: {self.pdf_output_file}'

        with open(self.pdf_output_file, 'rb') as f:
            contents = f.read()

        return True, contents

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
            stroke_color=self.color_crimson,
            fill_color=self.color_crimson,
        ).layout(page, r)

        line_height2 = 1
        r: Rectangle = Rectangle(Decimal(0),
                                 ps[1] - line_height - line_height2,
                                 ps[0], Decimal(line_height2))
        Shape(
            points=LineArtFactory.rectangle(r),
            stroke_color=HexColor("#000000"),
            fill_color=HexColor("#000000"),
        ).layout(page, r)
