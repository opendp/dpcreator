"""
Create a PDF report based on a DP Release
"""
from __future__ import annotations
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
from borb.pdf.canvas.layout.image.chart import Chart
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout

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
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.canvas.layout.table.flexible_column_width_table import FlexibleColumnWidthTable
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.color.color import HexColor

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
from opendp_apps.utils.randname import random_with_n_digits

class PDFReportMaker(BasicErrCheck):

    # basic_font = 'Times-roman'
    color_crimson = HexColor('#a41d30')
    basic_font = get_custom_font(OPEN_SANS_LIGHT)
    basic_font_italic = get_custom_font(OPEN_SANS_ITALIC)
    basic_font_bold = get_custom_font(OPEN_SANS_SEMI_BOLD)

    def __init__(self, release_dict: dict = None):
        """Initalize with a DP Release as Python dict"""
        self.release_dict = release_dict
        if not release_dict:
            self.release_dict = self.get_test_release()

        # Used to embed the JSON file contents directly to the PDF file
        self.release_json_bytes = bytes(json.dumps(self.release_dict, indent=4), encoding="latin1")

        # Set font sizes
        self.basic_font_size = Decimal(9)
        self.tbl_font_size = Decimal(9)
        self.tbl_border_color = HexColor("#cbcbcb")

        # param table
        self.indent1 = Decimal(10)
        self.indent2 = Decimal(20)

        # PDF file
        self.pdf_output_file = join(CURRENT_DIR,
                                    'test_data',
                                    'pdfs',
                                    'pdf_report_01_%s.pdf' % (random_with_n_digits(6)))

        ps: typing.Tuple[Decimal, Decimal] = PageSize.LETTER_PORTRAIT.value
        self.page_width, self.page_height = ps  # page width, height
        print(f'page_width/page_height: {self.page_width}/{self.page_height}')

        self.page_cnt = 0
        self.pdf_doc: Document = Document()
        self.current_page = None  # Page
        self.layout = None  # PageLayout

        self.creation_date = None

        self.format_release()

        self.create_pdf()

    def start_new_page(self):
        """Start a new page"""
        self.page_cnt += 1
        self.current_page = Page(PageSize.LETTER_PORTRAIT.value[0], PageSize.LETTER_PORTRAIT.value[1])
        self.pdf_doc.append_page(self.current_page)
        self.layout: PageLayout = SingleColumnLayout(self.current_page)

        # Add line at the top
        #
        self.add_header_border_logo(self.current_page)

    def add_to_layout(self, pdf_element):
        """Add a PDF element to the document"""
        try:
            self.layout.add(pdf_element)
        except AssertionError as ex_obj:
            print("The PDF doesn't fit!")
            print(ex_obj)
            assert_err1 = 'A Rectangle must have a non-negative height.'
            assert_err2 = 'FlexibleColumnWidthTable is too tall to fit inside column / page.'
            if str(ex_obj).find(assert_err1) > -1:
                print('AssertionError 1')
            elif str(ex_obj).find(assert_err2) > -1:
                print('AssertionError 2')

            print("Start a new page!")
            self.start_new_page()
            print('Try to add the element again')

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
        """Return a table cell aligned left with left padding"""
        return self._get_tbl_cell(content,
                                  self.basic_font,
                                  self.tbl_font_size,
                                  Alignment.LEFT,
                                  col_span=1,
                                  padding_left=padding)

    def get_tbl_cell_align_rt(self, content):
        """Return a table cell aligned right"""
        return self._get_tbl_cell(content, self.basic_font, self.tbl_font_size, Alignment.RIGHT)

    def _get_tbl_cell(self, content, font=None, font_size=None, text_alignment=None,
                      col_span=1, padding_left=0) -> TableCell:
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
                      text_alignment=text_alignment,
                      )
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
        self.start_new_page()

        # Add title text
        #
        title_text = render_to_string('pdf_report/10_title.txt', self.release_dict)
        self.add_to_layout(self.get_centered_para(title_text))

        # Add intro text
        #
        intro_text = render_to_string('pdf_report/intro_text.txt', self.release_dict)
        self.add_to_layout(Paragraph(intro_text,
                                     font=self.basic_font,
                                     font_size=self.basic_font_size,
                                     multiplied_leading=Decimal(1.75)))

        para_read_carefully = ('Please read the report carefully, especially in'
                               ' regard to usage of these statistics.')
        self.add_to_layout(Paragraph(para_read_carefully,
                                     font=self.basic_font,
                                     font_size=self.basic_font_size,
                                     multiplied_leading=Decimal(1.75)))

        self.add_to_layout(Paragraph('Contents',
                           font=get_custom_font(OPEN_SANS_SEMI_BOLD),
                           font_size=self.basic_font_size,
                           multiplied_leading=Decimal(1.75)))

        self.add_to_layout(self.txt_list_para('1. Statistics'))
        stat_cnt = 0
        for stat_info in self.release_dict['statistics']:
            stat_cnt += 1
            stat_type = stat_info['statistic']
            var_name = stat_info['variable']
            self.add_to_layout(self.txt_list_para(f'1.{stat_cnt}. {var_name} - {stat_type}', Decimal(60)))

        self.add_to_layout(self.txt_list_para('2. Data source'))
        self.add_to_layout(self.txt_list_para('3. OpenDP Library / Usage'))
        self.add_to_layout(self.txt_list_para('4. Parameter Definitions'))

        stat_cnt = 0
        for stat_info in self.release_dict['statistics']:
            if stat_info['statistic'] == astatic.DP_HISTOGRAM:
                continue
            # Put each statistic on a new page
            self.start_new_page()

            stat_cnt += 1
            stat_type = stat_info['statistic'].title()
            var_name = stat_info['variable']

            subtitle = f"1.{stat_cnt}. {var_name} - " + stat_type
            self.add_to_layout(Paragraph(subtitle,
                                         font=get_custom_font(OPEN_SANS_SEMI_BOLD),
                                         font_size=self.basic_font_size + Decimal(1),
                                         font_color=self.color_crimson,
                                         multiplied_leading=Decimal(1.75)))

            text_chunks_01 = [
                self.txt_bld('Result.'),
                self.txt_reg(f' A '),
                self.txt_bld(f'differentially private (DP) {stat_type}'),
                self.txt_reg(' has been calculated for the variable'),
                self.txt_bld(f" {var_name}."),
                self.txt_reg(' The result,'),
                self.txt_reg(' accuracy,'),
                self.txt_reg(' and a description are shown below:'),
            ]

            self.add_to_layout(HeterogeneousParagraph(text_chunks_01,
                                                      padding_left=Decimal(10)))

            if stat_info['statistic'] == astatic.DP_MEAN:

                self.add_single_stat_result_table(stat_info, stat_type, var_name)

                text_chunks_02 = [
                    self.txt_bld(f'Parameters.'),
                    self.txt_reg((' The table below shows the parameters used when'
                                  ' calculating the DP Mean. For reference, ')),
                    self.txt_reg(' a description of each'),
                    self.txt_reg(' parameter may be found at the end of the document.'),
                ]

                self.add_to_layout(HeterogeneousParagraph(text_chunks_02,
                                                          padding_left=Decimal(10)))

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
                table_001.set_border_color_on_all_cells(self.color_crimson)
                table_001.set_borders_on_all_cells(True, False, True, False)  # top, right, bottom, left

                rsize = self.get_layout_box(table_001)
                print('rsize: W x H', rsize.width, rsize.height)
                self.add_to_layout(table_001)

        self.add_to_layout(Chart(self.create_example_plot(),
                                 width=Decimal(450),
                                 height=Decimal(256)))

        # Add label for the PDF outline
        #
        self.pdf_doc.add_outline("Differentially Private Release", 0, DestinationType.FIT, page_nr=0)

        # Embed the JSON release in the PDF
        #
        self.pdf_doc.append_embedded_file("release_data.json", self.release_json_bytes)

        with open(self.pdf_output_file, "wb") as out_file_handle:
            PDF.dumps(out_file_handle, self.pdf_doc)
        print(f'PDF created: {self.pdf_output_file}')
        os.system(f'open {self.pdf_output_file}')

    def get_layout_box(self, p: Paragraph) -> Rectangle:
        """From https://stackoverflow.com/questions/69318059/create-documents-with-dynamic-height-with-borb"""
        pg: Page = Page()
        zero_dec: Decimal = Decimal(0)
        W: Decimal = Decimal(1000)  # max width you would allow
        H: Decimal = Decimal(1000)  # max height you would allow
        return p.layout(pg, Rectangle(zero_dec, zero_dec, W, H))

    def add_single_stat_result_table(self, stat_info: dict, stat_type: str, var_name: str):
        """
        Add the result table for a single stat, such as DP Mean. Example:
            DP Mean                 2.9442
            Accuracy                0.1964
            Confidence Level        95.0%
            Description             There is a probability of 95.0% that the ... (etc)
        """
        tbl_result = FlexibleColumnWidthTable(number_of_rows=4,
                                              number_of_columns=2,
                                              padding_left=Decimal(40),
                                              padding_right=Decimal(60),
                                              padding_bottom=Decimal(0),
                                              )
        # Statistic name and result
        tbl_result.add(self.get_tbl_cell_lft_pad(f'DP {stat_type}', padding=0))
        res_fmt = round(stat_info['result']['value'], 4)
        tbl_result.add(self.get_tbl_cell_align_rt(f"{res_fmt}"))

        # Accuracy
        tbl_result.add(self.get_tbl_cell_lft_pad("Accuracy", padding=0))
        acc_fmt = round(stat_info['accuracy']['value'], 4)
        tbl_result.add(self.get_tbl_cell_align_rt(f"{acc_fmt}"))

        # Confidence Level
        clevel = round(stat_info['confidence_level'] * 100.0, 1)
        tbl_result.add(self.get_tbl_cell_lft_pad("Confidence Level", padding=0))
        tbl_result.add(self.get_tbl_cell_align_rt(f"{clevel}%"))

        # Description
        #
        tbl_result.add(self.get_tbl_cell_lft_pad("Description", padding=0))

        acc_desc = (f'There is a probability of {clevel}% that the DP {stat_type} '
                    f' will differ'
                    f' from the true {stat_type} by at most {acc_fmt} units.'
                    f' The units are the same units the variable {var_name} has in the dataset.')

        tbl_result.add(self.get_tbl_cell_lft_pad(acc_desc))

        # Table, padding, border color, and borders
        tbl_result.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))
        tbl_result.set_border_color_on_all_cells(self.color_crimson)
        tbl_result.set_borders_on_all_cells(True, False, True, False)  # top, right, left, bottom

        self.add_to_layout(tbl_result)


    def get_pdf_contents(self):
        """Return the PDF contents"""
        if self.has_error():
            return False, self.get_err_msg()

        if not isfile(self.pdf_output_file):
            return False, f'Not a file: {self.pdf_output_file}'

        with open(self.pdf_output_file, 'rb') as f:
            contents = f.read()

        return True, contents

    @staticmethod
    def create_example_plot():
        """Example plot"""
        hist_vals = {'bins': list(range(1,13)),
                     'vals': [random.randint(1, 100) for _x in range(1, 13)],
                     }
        print('hist_vals', hist_vals)
        fig = MatPlotLibPlot.figure()
        ax = fig.add_subplot()
        ax.bar(x=hist_vals['bins'], height=hist_vals['vals'])
        ax.set_xlabel('Month')
        ax.set_ylabel('# Thunderstorms')

        # return the current figure
        return MatPlotLibPlot.gcf()

    def add_header_border_logo(self, page: Page) -> None:
        """
        Add a top crimson/black border to each page. Add the DP Creator logo to the 1st page
        """
        # --------------------------------
        # Add top crimson border
        # --------------------------------
        line_height = 16
        r: Rectangle = Rectangle(Decimal(0),  # lower_left_x
                                 self.page_height - line_height,  # lower_left_y
                                 self.page_width,  # width
                                 Decimal(line_height))  # height

        Shape(
            points=LineArtFactory.rectangle(r),
            stroke_color=self.color_crimson,
            fill_color=self.color_crimson,
        ).layout(page, r)

        # --------------------------------
        # Add top black border
        # --------------------------------
        line_height2 = 1
        r: Rectangle = Rectangle(Decimal(0),
                                 self.page_height - line_height - line_height2,
                                 self.page_width,
                                 Decimal(line_height2))
        Shape(
            points=LineArtFactory.rectangle(r),
            stroke_color=HexColor("#000000"),
            fill_color=HexColor("#000000"),
        ).layout(page, r)

        # --------------------------------
        # Add logo to the first page
        # --------------------------------
        if self.page_cnt == 1:
            logo_height = 32  # 64 / 2
            logo_width = 72  # 144 / 2
            rect_logo: Rectangle = Rectangle(Decimal(10),
                                             self.page_height - line_height - logo_height - Decimal(10),
                                             Decimal(logo_width),
                                             Decimal(logo_height))
            logo_img_obj = Image(
                DPCREATOR_LOGO_PATH,
                width=Decimal(logo_width),
                height=Decimal(logo_height),
            )

            logo_img_obj.layout(page, rect_logo)

            # Link logo to opendp.org url
            page.append_remote_go_to_annotation(logo_img_obj.get_bounding_box(),
                                                uri="https://www.opendp.org")
