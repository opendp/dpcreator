"""
Create a PDF report based on a DP Release
"""
from __future__ import annotations
from decimal import Decimal
import json

import os, sys
from os.path import abspath, dirname, isfile, join
import dateutil
import random
import typing

CURRENT_DIR = dirname(abspath(__file__))

from django.template.loader import render_to_string

from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.layout.image.chart import Chart
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout

from borb.pdf.document import Document
from borb.pdf.page.page import DestinationType
from borb.pdf.page.page import Page
from borb.pdf.page.page_size import PageSize
from borb.pdf.pdf import PDF
from borb.pdf.canvas.layout.text.chunks_of_text import HeterogeneousParagraph
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.line_art.line_art_factory import LineArtFactory
from borb.pdf.canvas.geometry.rectangle import Rectangle
from borb.pdf.canvas.layout.shape.shape import Shape
from borb.pdf.canvas.layout.table.flexible_column_width_table import FlexibleColumnWidthTable
from borb.pdf.canvas.layout.table.table import Table
from borb.pdf.canvas.color.color import HexColor

import matplotlib.pyplot as MatPlotLibPlot
import numpy as np
import pandas as pd
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.dp_reports import pdf_utils as putil

from opendp_apps.dp_reports import static_vals as pdf_static
from opendp_apps.utils.randname import random_with_n_digits

class PDFReportMaker(BasicErrCheck):

    def __init__(self, release_dict: dict = None):
        """Initalize with a DP Release as Python dict"""
        self.release_dict = release_dict
        if not release_dict:
            self.release_dict = self.get_test_release()

        # Used to embed the JSON file contents directly to the PDF file
        self.release_json_bytes = bytes(json.dumps(self.release_dict, indent=4), encoding="latin1")

        # num statistics
        self.num_stats = len(self.release_dict['statistics'])

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

    def create_pdf(self):
        """Start making the PDF"""
        self.add_pdf_title_page()

        self.add_statistics_pages()

        self.add_data_source_and_lib()

        # test chart
        # self.add_to_layout(Chart(self.create_example_plot(), width=Decimal(450), height=Decimal(256)))

        # Add label for the PDF outline
        #
        self.pdf_doc.add_outline("Differentially Private Release", 0, DestinationType.FIT, page_nr=0)
        self.pdf_doc.add_outline("Statistics", 1, DestinationType.FIT, page_nr=1)
        self.pdf_doc.add_outline("Data Source", 1, DestinationType.FIT, page_nr=self.page_cnt - 1)

        self.embed_json_release_in_pdf()

        with open(self.pdf_output_file, "wb") as out_file_handle:
            PDF.dumps(out_file_handle, self.pdf_doc)
        print(f'PDF created: {self.pdf_output_file}')
        os.system(f'open {self.pdf_output_file}')

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

    @staticmethod
    def get_test_release():
        """for dev/building"""
        # test_release_name = join(CURRENT_DIR, 'test_data', 'sample_release_01.json')
        test_release_name = join(CURRENT_DIR, 'test_data', 'release_f082cbc4-9cd7-4e44-a0f3-f4ad967f237c.json')

        return json.loads(open(test_release_name, 'r').read())

    def embed_json_release_in_pdf(self):
        """Embed the JSON release in the PDF"""
        self.pdf_doc.append_embedded_file("release_data.json", self.release_json_bytes)

    def get_general_stat_result_desc(self, stat_type_formatted, var_name) -> list:
        """Return the general "Result" description"""
        text_chunks = [
            putil.txt_bld('Result.'),
            putil.txt_reg(f' A '),
            putil.txt_bld(f'DP {stat_type_formatted}'),
            putil.txt_reg(' has been calculated for the variable'),
            putil.txt_bld(f" {var_name}."),
            putil.txt_reg(' The result,'),
            putil.txt_reg(' accuracy,'),
            putil.txt_reg(' and a description are shown below:'),
        ]
        return text_chunks

    def get_histogram_stat_result_desc(self, stat_type_formatted: str, var_name: str) -> list:
        """Return the general "Result" description"""
        text_chunks = [
            putil.txt_bld('Result.'),
            putil.txt_reg(f' A '),
            putil.txt_bld(f'DP {stat_type_formatted}'),
            putil.txt_reg(' has been calculated for the variable'),
            putil.txt_bld(f" {var_name}."),
            putil.txt_reg(' The histogram'),
            putil.txt_reg(' is shown below:'),
            # putil.txt_reg(' and table are shown below:'),
        ]
        return text_chunks

    def get_histogram_accuracy_desc(self, stat_type_formatted: str, var_name: str) -> list:
        """Return the general "Result" description"""
        text_chunks = [
            putil.txt_bld('Result (continued).'),
            putil.txt_reg(f' A '),
            putil.txt_bld(f'DP {stat_type_formatted}'),
            putil.txt_reg(' has been calculated for the variable'),
            putil.txt_bld(f" {var_name}."),
            putil.txt_reg(' The histogram'),
            putil.txt_reg(' result and accuracy information is shown below.'),
            # putil.txt_reg(' and table are shown below:'),
        ]
        return text_chunks

    def add_statistics_pages(self):
        """Add a page for each DP statistic"""
        stat_cnt = 0
        for stat_info in self.release_dict['statistics']:
            # Put each statistic on a new page
            self.start_new_page()

            stat_cnt += 1
            stat_type = stat_info['statistic']
            stat_type_formatted = stat_type.title()
            var_name = stat_info['variable']

            subtitle = f"1.{stat_cnt}. {var_name} - " + stat_type

            self.add_to_layout(putil.txt_subtitle_para(subtitle))

            if stat_type in [astatic.DP_MEAN, astatic.DP_VARIANCE, astatic.DP_COUNT]:

                # add descriptive text
                stat_desc = self.get_general_stat_result_desc(stat_type_formatted, var_name)
                self.add_to_layout(HeterogeneousParagraph(stat_desc,
                                                          padding_left=Decimal(10)))

                # Add result table
                self.add_single_stat_result_table(stat_info, stat_type_formatted, var_name)

                # Add parameter info
                self.add_parameter_info(stat_info, stat_type_formatted)

            elif stat_type == astatic.DP_HISTOGRAM:

                # add descriptive text
                stat_desc = self.get_histogram_stat_result_desc(stat_type_formatted, var_name)
                self.add_to_layout(HeterogeneousParagraph(stat_desc,
                                                          padding_left=Decimal(10)))

                # show histogram
                self.add_histogram_plot(stat_info, var_name)

                # on a new page, show the metadata parameters
                self.start_new_page()  # new page

                # page heading
                subtitle2 = f"{subtitle} (continued)"
                self.add_to_layout(putil.txt_subtitle_para(subtitle2))

                stat_desc = self.get_histogram_accuracy_desc(stat_type_formatted, var_name)
                self.add_to_layout(HeterogeneousParagraph(stat_desc,
                                                          padding_left=Decimal(10)))

                # Add result table
                self.add_histogram_result_table(stat_info, stat_type_formatted, var_name)

                # parameter info
                self.add_parameter_info(stat_info, stat_type_formatted)

    def add_histogram_plot(self, stat_info: dict, var_name: str):
        """
        Create a plot from histogram data and add it to the layout
        ref: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar.html#matplotlib.axes.Axes.bar
        """
        if self.has_error():
            return
        assert stat_info['statistic'] == astatic.DP_HISTOGRAM, \
            f"This method should only be used for Histograms. Not statistic: \"{stat_info['statistic']}\""

        # -------------------------------------
        # Get the x/y data!
        # -------------------------------------
        hist_bins = stat_info['result']['value']['categories']
        hist_vals = stat_info['result']['value']['values']

        # -------------------------------------
        # Set the bins to string format.
        #  e.g. the last value is "uncategorized" and errors occur if numerics/strings are mixed
        # -------------------------------------
        hist_bins = [str(x) for x in hist_bins]

        # -------------------------------------
        # Make a bar lot
        # -------------------------------------
        fig = MatPlotLibPlot.figure(tight_layout=True, figsize=[8,6])
        ax = fig.add_subplot()

        # -------------------------------------
        # Check if the labels overlap
        #   (very rough/naive!)
        # -------------------------------------

        # What's the longest bin label? (Not counting the last bin of "uncategorized")
        max_bin_length = max([len(x) for x in hist_bins[:-1]])

        # Rotate the labels so they don't overlap
        if len(hist_vals) > 10 and max_bin_length > 2:
            MatPlotLibPlot.xticks(rotation=90, ha='right')

        # -------------------------------------
        # Set the bar colors
        # -------------------------------------
        bar_container_obj = ax.bar(x=hist_bins,
                                   height=hist_vals,
                                   color="#6395e3",
                                   edgecolor="#333333",
                                   )

        # Set the "uncategorized" bin/bar to a different color
        bar_container_obj.patches[-1].set_facecolor('#C5C5C5')

        # -------------------------------------
        # Add title and x/y labels
        # -------------------------------------
        ax.set_title(f'DP Histogram of "{var_name}"')
        ax.set_xlabel(var_name)
        ax.set_ylabel('Count')

        # -------------------------------------
        # Add a threshold line if there are
        #  values < 0 (also naive)
        # -------------------------------------
        # horizontal line indicating the threshold
        if min(hist_vals) < 0:
            ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
            #ax.plot([0., 4.5], [0, 0], "k--")

            # If there are negative values--except the last "uncategorized value", change the color
            for idx, patch in enumerate(bar_container_obj.patches[:-1]):
                if hist_vals[idx] < 0:
                    patch.set_facecolor('#f4d493')

        # -------------------------------------
        # Add the chart to the layout
        # -------------------------------------
        self.add_to_layout(Chart(MatPlotLibPlot.gcf(),
                                 width=Decimal(450),
                                 height=Decimal(256)))

        """
        fig = plt.figure(tight_layout=True, figsize=self.figure_size)
        ax = fig.add_subplot()
        ax.bar(x=statistic['result']['categories'], height=statistic['result']['value'])
        ax.set_xlabel(statistic['variable'])
        filename = '_'.join([statistic['variable'], statistic['statistic']])
        fig.savefig('./images/' + filename + '.png')
        """


    def add_parameter_info(self, stat_info: dict, stat_type_formatted: str):
        """Add parameter information, including epsilon, bounds, etc."""
        if self.has_error():
            return

        # --------------------------------------
        # Add parameter text
        # --------------------------------------
        text_chunks_02 = [
            putil.txt_bld(f'Parameters.'),
            putil.txt_reg((f' The table below shows the parameters used when'
                           f' calculating the DP {stat_type_formatted}. For reference, ')),
            putil.txt_reg(' a description of each'),
            putil.txt_reg(' parameter may be found at the end of the document.'),
        ]
        self.add_to_layout(HeterogeneousParagraph(text_chunks_02,
                                                  padding_left=Decimal(10)))

        # --------------------------------------
        # Create table for parameters
        # --------------------------------------
        is_dp_count = False
        if stat_info['statistic'] == astatic.DP_COUNT:
            is_dp_count = True
            num_param_table_rows = 5
        else:
            num_param_table_rows = 11

        # Create basic table
        #
        table_001 = FlexibleColumnWidthTable(number_of_rows=num_param_table_rows,
                                             number_of_columns=2,
                                             padding_left=Decimal(40),
                                             padding_right=Decimal(40),
                                             border_color=putil.COLOR_CRIMSON)

        # Add Privacy Parameters
        #
        table_001.add(putil.get_tbl_cell_ital("Privacy Parameters", col_span=2))

        table_001.add(putil.get_tbl_cell_lft_pad("Epsilon", padding=20))
        table_001.add(putil.get_tbl_cell_align_rt(f"{stat_info['epsilon']}"))

        table_001.add(putil.get_tbl_cell_lft_pad("Delta", padding=20))
        delta_val = stat_info['delta']
        if delta_val is None:
            delta_val = '(not applicable)'
        table_001.add(putil.get_tbl_cell_align_rt(f'{delta_val}'))

        table_001.add(putil.get_tbl_cell_ital("Metadata Parameters", col_span=2))

        if not is_dp_count:
            table_001.add(putil.get_tbl_cell_ital("Bounds", col_span=2, padding=20))

            table_001.add(putil.get_tbl_cell_lft_pad("Min", padding=40))
            table_001.add(putil.get_tbl_cell_align_rt(f"{stat_info['bounds']['min']}"))

            table_001.add(putil.get_tbl_cell_lft_pad("Max", padding=40))
            table_001.add(putil.get_tbl_cell_align_rt(f"{stat_info['bounds']['max']}"))

        table_001.add(putil.get_tbl_cell_lft_pad("Confidence Level", padding=20))
        table_001.add(putil.get_tbl_cell_align_rt(f"{stat_info['confidence_level']}"))

        # Add Missing Value Handling
        #
        if not is_dp_count:
            table_001.add(putil.get_tbl_cell_ital("Missing Value Handling", col_span=2))

            table_001.add(putil.get_tbl_cell_lft_pad("Type", padding=20))
            missing_val_handling = stat_info['missing_value_handling']['type']

            if missing_val_handling == astatic.MISSING_VAL_INSERT_FIXED:
                table_001.add(putil.get_tbl_cell_lft_pad(
                    astatic.missing_val_label(astatic.MISSING_VAL_INSERT_FIXED)))

                table_001.add(putil.get_tbl_cell_lft_pad("Value", padding=20))
                table_001.add(putil.get_tbl_cell_align_rt(
                    f"{stat_info['missing_value_handling']['fixed_value']}"))
            else:
                mval_text = (f'Fix! Unhandled missing value handling. ({missing_val_handling})')
                table_001.add(putil.get_tbl_cell_ital(mval_text, col_span=2))

        self.set_table_borders_padding(table_001)

        # rsize = self.get_layout_box(table_001)
        # print('rsize: W x H', rsize.width, rsize.height)
        self.add_to_layout(table_001)

    def set_table_borders_padding(self, table_obj: Table):
        """Add cell padding and top/bottom borders. The border color is crimson"""
        if self.has_error():
            return

        table_obj.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))
        table_obj.set_border_color_on_all_cells(putil.COLOR_CRIMSON)
        table_obj.set_borders_on_all_cells(True, False, True, False)  # top, right, bottom, left

    def add_data_source_and_lib(self):
        """Add the data source and library information"""
        if self.has_error():
            return

        self.start_new_page()

        subtitle = f"2. Data Source"
        self.add_to_layout(putil.txt_subtitle_para(subtitle))

        basic_desc = render_to_string('pdf_report/20_data_source_desc.txt',
                                      self.release_dict)

        self.add_to_layout(putil.txt_reg_para(basic_desc))

        dataset_info = self.release_dict['dataset']

        # Assuming a Dataverse dataset for now
        if dataset_info['type'] != 'dataverse':
            note = '!Not a Dataverse dataset. Add handling! (pdf_report_maker.py / add_data_source_and_lib)'
            self.add_to_layout(putil.txt_reg_para(note))
            return

        tbl_src = FlexibleColumnWidthTable(number_of_rows=11,
                                           number_of_columns=2,
                                           padding_left=Decimal(40),
                                           padding_right=Decimal(60),
                                           padding_bottom=Decimal(0))

        # ------------------------------
        # Dataverse - general info
        # ------------------------------
        tbl_src.add(putil.get_tbl_cell_ital("Dataverse Repository", col_span=2))

        tbl_src.add(putil.get_tbl_cell_lft_pad(f'Name', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad(f"{dataset_info['installation']['name']}", padding=0))

        tbl_src.add(putil.get_tbl_cell_lft_pad(f'URL', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad(f"{dataset_info['installation']['url']}", padding=0))

        # ------------------------------
        # Dataverse Dataset information
        # ------------------------------
        tbl_src.add(putil.get_tbl_cell_ital("Dataverse Dataset/Collection", col_span=2))

        tbl_src.add(putil.get_tbl_cell_lft_pad(f'Name', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad(f"{dataset_info['name']}", padding=0))
        citation_str = dataset_info['citation']
        if not citation_str:
            citation_str = '(not available)'
        tbl_src.add(putil.get_tbl_cell_lft_pad(f'Citation', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad(citation_str, padding=0))

        doi_str = dataset_info['doi']
        if not doi_str:
            doi_str = '(not available)'
        tbl_src.add(putil.get_tbl_cell_lft_pad(f'DOI', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad(doi_str, padding=0))

        # ------------------------------
        # File information
        # ------------------------------
        tbl_src.add(putil.get_tbl_cell_ital("File Information", col_span=2))
        tbl_src.add(putil.get_tbl_cell_lft_pad(f'Name', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad(f"{dataset_info['file_information']['name']}", padding=0))

        identifier_str = dataset_info['file_information']['identifier']
        if not identifier_str:
            identifier_str = '(not available)'
        tbl_src.add(putil.get_tbl_cell_lft_pad(f'Identifier', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad(identifier_str, padding=0))

        format_str = dataset_info['file_information']['fileFormat']
        if not format_str:
            format_str = '(not available)'
        tbl_src.add(putil.get_tbl_cell_lft_pad(f'File format', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad(format_str, padding=0))

        tbl_src.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))
        tbl_src.set_border_color_on_all_cells(putil.COLOR_CRIMSON)
        tbl_src.set_borders_on_all_cells(True, False, True, False)  # top, right, bottom, left

        self.set_table_borders_padding(tbl_src)
        self.add_to_layout(tbl_src)

        self.add_opendp_lib_info()

    def add_opendp_lib_info(self):
        """Add information about the OpenDP library (added to same page as data source info"""
        if self.has_error():
            return

        dp_lib_info = self.release_dict['differentially_private_library']

        # Subtitle and basic description
        #
        subtitle = f"3. OpenDP Library"
        self.add_to_layout(putil.txt_subtitle_para(subtitle))

        basic_desc = render_to_string('pdf_report/30_opendp_lib_desc.txt',
                                      self.release_dict)
        self.add_to_layout(putil.txt_reg_para(basic_desc))

        # Information table
        #
        tbl_src = FlexibleColumnWidthTable(number_of_rows=4,
                                           number_of_columns=2,
                                           padding_left=Decimal(40),
                                           padding_right=Decimal(60),
                                           padding_bottom=Decimal(0))

        tbl_src.add(putil.get_tbl_cell_ital("OpenDP Library", col_span=2))

        tbl_src.add(putil.get_tbl_cell_lft_pad(f'Version', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad(f"{dp_lib_info['version']}", padding=0))

        tbl_src.add(putil.get_tbl_cell_lft_pad(f'Python package', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad('https://pypi.org/project/opendp/', padding=0))

        tbl_src.add(putil.get_tbl_cell_lft_pad(f'GitHub Repository', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad(f"{dp_lib_info['url']}", padding=0))

        tbl_src.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))
        tbl_src.set_border_color_on_all_cells(putil.COLOR_CRIMSON)
        tbl_src.set_borders_on_all_cells(True, False, True, False)  # top, right, bottom, left

        self.set_table_borders_padding(tbl_src)

        self.add_to_layout(tbl_src)

    def add_pdf_title_page(self):
        """Add the PDF title page"""
        if self.has_error():
            return

        self.start_new_page()

        # Add title text
        #
        title_text = render_to_string('pdf_report/10_title.txt', self.release_dict)
        self.add_to_layout(putil.get_centered_para(title_text))

        # Add intro text
        #
        intro_text = render_to_string('pdf_report/intro_text.txt', self.release_dict)
        self.add_to_layout(Paragraph(intro_text,
                                     font=putil.BASIC_FONT,
                                     font_size=putil.BASIC_FONT_SIZE,
                                     multiplied_leading=Decimal(1.75)))

        para_read_carefully = ('Please read the report carefully, especially in'
                               ' regard to the usage of these statistics.')
        self.add_to_layout(Paragraph(para_read_carefully,
                                     font=putil.BASIC_FONT,
                                     font_size=putil.BASIC_FONT_SIZE,
                                     multiplied_leading=Decimal(1.75)))

        para_attachment = ('Note: If you are using Adobe Acrobat, a JSON version of this data'
                           ' is attached to this PDF as a file named "release_data.json".')

        self.add_to_layout(Paragraph(para_attachment,
                                     font=putil.BASIC_FONT,
                                     font_size=putil.BASIC_FONT_SIZE,
                                     multiplied_leading=Decimal(1.75)))

        self.add_to_layout(Paragraph('Contents',
                           font=putil.BASIC_FONT_BOLD,
                           font_size=putil.BASIC_FONT_SIZE,
                           multiplied_leading=Decimal(1.75)))

        self.add_to_layout(putil.txt_list_para('1. Statistics'))
        stat_cnt = 0
        for stat_info in self.release_dict['statistics']:
            stat_cnt += 1
            stat_type = 'DP ' + stat_info['statistic'].title()
            var_name = stat_info['variable']
            self.add_to_layout(putil.txt_list_para(f'1.{stat_cnt}. {var_name} - {stat_type}', Decimal(60)))

        self.add_to_layout(putil.txt_list_para('2. Data Source'))
        self.add_to_layout(putil.txt_list_para('3. OpenDP Library'))
        self.add_to_layout(putil.txt_list_para('4. Usage'))
        self.add_to_layout(putil.txt_list_para('5. Parameter Definitions'))

    @staticmethod
    def get_layout_box(p: Paragraph) -> Rectangle:
        """From https://stackoverflow.com/questions/69318059/create-documents-with-dynamic-height-with-borb"""
        pg: Page = Page()
        zero_dec: Decimal = Decimal(0)
        _width: Decimal = Decimal(1000)  # max width you would allow
        _height: Decimal = Decimal(1000)  # max height you would allow
        return p.layout(pg, Rectangle(zero_dec, zero_dec, _width, _height))

    def add_histogram_result_table(self, stat_info: dict, stat_type: str, var_name: str):
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
        tbl_result.add(putil.get_tbl_cell_lft_pad(f'DP {stat_type}', padding=0))
        categories = stat_info['result']['value']['categories']
        result_text = 'The results, in JSON format, may accessed through the PDF attachemnt "release_data.json"'
        if len(categories) ==  1:
            tbl_result.add(putil.get_tbl_cell_lft_pad(f"(1 bin/category). {result_text}", padding=0))
        else:
            tbl_result.add(putil.get_tbl_cell_lft_pad(f"({len(categories)} bins/categories). {result_text}",
                                                      padding=0))

        # Accuracy
        tbl_result.add(putil.get_tbl_cell_lft_pad("Accuracy", padding=0))
        acc_fmt = round(stat_info['accuracy']['value'], 4)
        tbl_result.add(putil.get_tbl_cell_align_rt(f"{acc_fmt}"))

        # Confidence Level
        clevel = round(stat_info['confidence_level'] * 100.0, 1)
        tbl_result.add(putil.get_tbl_cell_lft_pad("Confidence Level", padding=0))
        tbl_result.add(putil.get_tbl_cell_align_rt(f"{clevel}%"))

        # Description
        #
        tbl_result.add(putil.get_tbl_cell_lft_pad("Description", padding=0))

        acc_desc = (f'There is a probability of {clevel}% that a count on the DP {stat_type} '
                    f' will differ'
                    f' from the true {stat_type} by at most {acc_fmt} units.'
                    f' The units are the same units the variable {var_name} has in the dataset.')

        tbl_result.add(putil.get_tbl_cell_lft_pad(acc_desc))

        # Table, padding, border color, and borders
        tbl_result.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))
        tbl_result.set_border_color_on_all_cells(putil.COLOR_CRIMSON)
        tbl_result.set_borders_on_all_cells(True, False, True, False)  # top, right, left, bottom

        self.set_table_borders_padding(tbl_result)

        self.add_to_layout(tbl_result)

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
        tbl_result.add(putil.get_tbl_cell_lft_pad(f'DP {stat_type}', padding=0))
        res_fmt = round(stat_info['result']['value'], 4)
        tbl_result.add(putil.get_tbl_cell_align_rt(f"{res_fmt}"))

        # Accuracy
        tbl_result.add(putil.get_tbl_cell_lft_pad("Accuracy", padding=0))
        acc_fmt = round(stat_info['accuracy']['value'], 4)
        tbl_result.add(putil.get_tbl_cell_align_rt(f"{acc_fmt}"))

        # Confidence Level
        clevel = round(stat_info['confidence_level'] * 100.0, 1)
        tbl_result.add(putil.get_tbl_cell_lft_pad("Confidence Level", padding=0))
        tbl_result.add(putil.get_tbl_cell_align_rt(f"{clevel}%"))

        # Description
        #
        tbl_result.add(putil.get_tbl_cell_lft_pad("Description", padding=0))

        acc_desc = (f'There is a probability of {clevel}% that the DP {stat_type} '
                    f' will differ'
                    f' from the true {stat_type} by at most {acc_fmt} units.'
                    f' The units are the same units the variable {var_name} has in the dataset.')

        tbl_result.add(putil.get_tbl_cell_lft_pad(acc_desc))

        # Table, padding, border color, and borders
        tbl_result.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))
        tbl_result.set_border_color_on_all_cells(putil.COLOR_CRIMSON)
        tbl_result.set_borders_on_all_cells(True, False, True, False)  # top, right, left, bottom

        self.set_table_borders_padding(tbl_result)

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
        hist_vals = {'bins': list(range(1, 13)),
                     'vals': [random.randint(1, 100) for _x in range(1, 13)]}
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
            stroke_color=putil.COLOR_CRIMSON,
            fill_color=putil.COLOR_CRIMSON,
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
                pdf_static.DPCREATOR_LOGO_PATH,
                width=Decimal(logo_width),
                height=Decimal(logo_height),
            )

            logo_img_obj.layout(page, rect_logo)

            # Link logo to opendp.org url
            page.append_remote_go_to_annotation(logo_img_obj.get_bounding_box(),
                                                uri="https://www.opendp.org")
