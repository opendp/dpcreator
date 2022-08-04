"""
Create a PDF report based on a DP Release
"""
from __future__ import annotations

import copy
import io
import json
import logging
import os
import random
import typing
import uuid
from decimal import Decimal
from os.path import abspath, dirname, isfile, join

CURRENT_DIR = dirname(abspath(__file__))

from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string

from borb.pdf.canvas.layout.annotation.link_annotation import (
    LinkAnnotation,
    DestinationType,
)
from borb.pdf.canvas.layout.annotation.remote_go_to_annotation import RemoteGoToAnnotation
from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.layout.image.chart import Chart
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout

from borb.pdf.document.document import Document
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
from opendp_apps.analysis import static_vals as astatic

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck

from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.dp_reports import pdf_preset_text
from opendp_apps.dp_reports import pdf_utils as putil
from opendp_apps.dp_reports import static_vals as pdf_static
from opendp_apps.analysis.models import ReleaseInfo
from opendp_apps.profiler.static_vals import VAR_TYPE_CATEGORICAL
from opendp_apps.utils.randname import random_with_n_digits

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class PDFReportMaker(BasicErrCheck):
    SECTION_TITLE_01_STATISTICS = '1. Statistics'
    SECTION_TITLE_02_DATA_SOURCE = '2. Data Source'
    SECTION_TITLE_03_OPENDP_LIB = '3. OpenDP Library'
    SECTION_TITLE_04_USAGE = '4. Parameter Definitions'
    SECTION_TITLE_05_NEGATIVE_VALUES = '5. Negative Values'

    def __init__(self, release_dict: dict = None, release_object_id: typing.Union[uuid.uuid4, str] = None):
        """Initalize with a DP Release as Python dict"""
        if not release_dict:
            self.release_dict = self.get_test_release()
        else:
            self.release_dict = copy.deepcopy(release_dict)

        self.release_object_id = release_object_id

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
        self.page_width, self.page_height = ps

        self.page_cnt = 0
        self.pdf_doc: Document = Document()
        self.first_page = None
        self.current_page = None  # Page
        self.layout = None  # PageLayout

        self.creation_date = None
        self.intrapage_link_info = []  # [[text to link, pdf_object_ref, pdf_page_num, indent], etc.]

        self.format_release()

        self.create_pdf()

    def create_pdf(self):
        """Start making the PDF"""
        self.add_pdf_title_page()

        self.add_statistics_pages()

        self.add_data_source_and_lib()

        self.add_usage_page()

        self.add_negative_values()

        # test chart
        # self.add_to_layout(Chart(self.create_example_plot(), width=Decimal(450), height=Decimal(256)))

        # Add label for the PDF outline
        #
        self.pdf_doc.add_outline("Differentially Private Release", 0, DestinationType.FIT, page_nr=0)
        self.pdf_doc.add_outline("Statistics", 1, DestinationType.FIT, page_nr=1)
        self.pdf_doc.add_outline("Data Source", 1, DestinationType.FIT, page_nr=self.page_cnt - 1)

        self.add_intra_page_links()  # links within the document
        self.embed_json_release_in_pdf()

    def save_pdf_to_release_obj(self, release_info_obj: ReleaseInfo):
        """Save the PDF to the FileField: ReleaseInfo.dp_release_pdf_file"""
        if self.has_error():
            return

        # Write PDF doc to BytesIO
        #
        pdf_bytes = io.BytesIO()
        PDF.dumps(pdf_bytes, self.pdf_doc)
        pdf_bytes.seek(0)  # rewind to the start!

        # Save the PDF bytes to a Django FileField
        #
        pdf_fname = f'release_{release_info_obj.object_id}.pdf'

        release_info_obj.dp_release_pdf_file.save(pdf_fname,
                                                  ContentFile(pdf_bytes.read()),
                                                  save=True)

        # release_info_obj.save()
        logger.info(f'File saved to release: {release_info_obj.dp_release_pdf_file}')

    def get_embed_json_fname(self):
        """Get the name of the JSON file embedded in the PDF"""
        if self.release_object_id:
            return f'release_data_{self.release_object_id}.json'

        return 'release_data.json'

    def save_intrapage_link(self, _txt_to_link: str, pdf_object_ref,
                            pdf_page_num: int, indent: int = pdf_static.TOC_L2_LINK_OFFSET):
        """
        Collect in-page links to hook up at the end of the process
        Note: pdf_page_num input should be 1-indexed. 
        """
        if self.has_error():
            return

        self.intrapage_link_info.append([_txt_to_link, pdf_object_ref, pdf_page_num, indent])

    def save_pdf_to_file(self, pdf_output_file: str = None):
        """Save the PDF to a file using the given name. Used for debugging."""
        if self.has_error():
            return

        self.pdf_output_file = pdf_output_file

        if not self.pdf_output_file:
            self.pdf_output_file = join(CURRENT_DIR,
                                        'test_data',
                                        'pdfs',
                                        'pdf_report_01_%s.pdf' % (random_with_n_digits(6)))

        print('pdf_output_file', self.pdf_output_file)
        with open(self.pdf_output_file, "wb") as out_file_handle:
            PDF.dumps(out_file_handle, self.pdf_doc)
        logger.info(f'PDF created: {self.pdf_output_file}')
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

        # Keep a pointer to the first page
        if self.page_cnt == 1:
            self.first_page = self.current_page

    def add_to_layout(self, pdf_element):
        """Add a PDF element to the document"""
        try:
            self.layout.add(pdf_element)
        except AssertionError as ex_obj:
            logger.exception("The PDF doesn't fit! %s", ex_obj)
            assert_err1 = 'A Rectangle must have a non-negative height.'
            assert_err2 = 'FlexibleColumnWidthTable is too tall to fit inside column / page.'
            if str(ex_obj).find(assert_err1) > -1:
                logger.exception('AssertionError 1')
            elif str(ex_obj).find(assert_err2) > -1:
                logger.exception('AssertionError 2')

            logger.info("(Recovering from error) Start a new page!")
            self.start_new_page()
            logger.info('Try to add the element again')

    def format_release(self):
        """Update release values"""
        pass
        # self.creation_date = dateutil.parser.parse(self.release_dict['created']['iso'])
        # self.release_dict['creation_date'] = self.creation_date

    @staticmethod
    def get_test_release():
        """for dev/building"""
        # test_release_name = join(CURRENT_DIR, 'test_data', 'sample_release_01.json')
        test_release_name = join(CURRENT_DIR, 'test_data', 'release_f082cbc4-9cd7-4e44-a0f3-f4ad967f237c.json')

        return json.loads(open(test_release_name, 'r').read())

    def embed_json_release_in_pdf(self):
        """Embed the JSON release in the PDF"""
        self.pdf_doc.append_embedded_file(self.get_embed_json_fname(),
                                          self.release_json_bytes)

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

    @staticmethod
    def get_histogram_accuracy_desc(stat_type_formatted: str, var_name: str) -> list:
        """Return the general "Result" description"""
        text_chunks = [
            putil.txt_bld('Result (continued).'),
            putil.txt_reg(f' A '),
            putil.txt_bld(f'DP {stat_type_formatted}'),
            putil.txt_reg(' has been calculated for the variable'),
            putil.txt_bld(f" {var_name}."),
            putil.txt_reg(' The histogram'),
            putil.txt_reg(' result and accuracy information are shown below.'),
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
        fig = MatPlotLibPlot.figure(tight_layout=True, figsize=[8, 6])
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
        has_negative_values = False
        if min(hist_vals) < 0:
            has_negative_values = True
            ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
            # ax.plot([0., 4.5], [0, 0], "k--")

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

        # If applicable, add negative value note
        if has_negative_values:
            text_chunks = [
                putil.txt_bld('Negative values.'),
                putil.txt_reg(f' The histogram contains negative values. For more information on how to use '),
                putil.txt_reg(f' this data, please see the section'),
                putil.txt_bld(f' {self.SECTION_TITLE_05_NEGATIVE_VALUES}'),
            ]

            self.add_to_layout(HeterogeneousParagraph(text_chunks,
                                                      padding_left=Decimal(10)))

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
        skip_bounds = False
        is_dp_count = False
        if stat_info['statistic'] == astatic.DP_COUNT:
            is_dp_count = True
            skip_bounds = True
            num_param_table_rows = 4
        elif stat_info['variable_type'] == VAR_TYPE_CATEGORICAL:
            skip_bounds = True
            num_param_table_rows = 7
        else:
            num_param_table_rows = 10

        delta_val = stat_info['delta']
        if not delta_val:
            num_param_table_rows -= 1

        # Create basic table
        #
        table_001 = FlexibleColumnWidthTable(number_of_rows=num_param_table_rows,
                                             number_of_columns=2,
                                             padding_left=Decimal(40),
                                             padding_right=Decimal(40),
                                             border_color=putil.COLOR_CRIMSON)

        # Add Privacy Parameters
        #
        if delta_val:
            priv_param_title = "Privacy Parameters"
        else:
            priv_param_title = "Privacy Parameter"

        table_001.add(putil.get_tbl_cell_ital(priv_param_title, col_span=2))

        table_001.add(putil.get_tbl_cell_lft_pad("Epsilon", padding=20))
        table_001.add(putil.get_tbl_cell_align_rt(f"{stat_info['epsilon']}"))

        # Delta
        if delta_val:
            table_001.add(putil.get_tbl_cell_lft_pad("Delta", padding=20))
            table_001.add(putil.get_tbl_cell_align_rt(f'{delta_val}'))

        table_001.add(putil.get_tbl_cell_ital("Metadata Parameters", col_span=2))

        if not skip_bounds:
            table_001.add(putil.get_tbl_cell_ital("Bounds", col_span=2, padding=20))

            table_001.add(putil.get_tbl_cell_lft_pad("Min", padding=40))
            table_001.add(putil.get_tbl_cell_align_rt(f"{stat_info['bounds']['min']}"))

            table_001.add(putil.get_tbl_cell_lft_pad("Max", padding=40))
            table_001.add(putil.get_tbl_cell_align_rt(f"{stat_info['bounds']['max']}"))

        # table_001.add(putil.get_tbl_cell_lft_pad("Confidence Level", padding=20))
        # table_001.add(putil.get_tbl_cell_align_rt(f"{stat_info['confidence_level']}"))

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
                mval_text = (f'Fix! Unhandled missing value handling.'
                             f' ({missing_val_handling})')
                table_001.add(putil.get_tbl_cell_ital(mval_text, col_span=2))

        self.set_table_borders_padding(table_001)

        self.add_to_layout(table_001)

    def set_table_borders_padding(self, table_obj: Table):
        """Add cell padding and top/bottom borders. The border color is crimson"""
        if self.has_error():
            return

        table_obj.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))
        table_obj.set_border_color_on_all_cells(putil.COLOR_CRIMSON)
        table_obj.set_borders_on_all_cells(True, False, True, False)  # t, r, b, l

    def add_usage_page(self):
        """Add page(s) on usage"""
        if self.has_error():
            return

        self.start_new_page()  # 1st page of Parameter definitions
        self.add_to_layout(putil.txt_subtitle_para(self.SECTION_TITLE_04_USAGE))
        for paragraph_obj in pdf_preset_text.PARAMETERS_AND_BOUNDS_01:
            self.add_to_layout(paragraph_obj)

        self.start_new_page()  # 2nd page of Parameter definitions
        for paragraph_obj in pdf_preset_text.PARAMETERS_AND_BOUNDS_02:
            self.add_to_layout(paragraph_obj)

    def add_negative_values(self):
        """Add page(s) on negative values"""
        if self.has_error():
            return

        self.start_new_page()

        self.add_to_layout(putil.txt_subtitle_para(self.SECTION_TITLE_05_NEGATIVE_VALUES))

        for paragraph_obj in pdf_preset_text.NEGATIVE_VALUES:
            self.add_to_layout(paragraph_obj)

    def add_dataset_upload_info(self, dataset_info):
        """Data Source section, add UploadFile table"""
        if self.has_error():
            return

        tbl_src = FlexibleColumnWidthTable(number_of_rows=6,
                                           number_of_columns=2,
                                           padding_left=Decimal(40),
                                           padding_right=Decimal(60),
                                           padding_bottom=Decimal(0))

        # ------------------------------
        # File information
        # ------------------------------
        tbl_src.add(putil.get_tbl_cell_ital("File Information", col_span=2))

        # Name
        tbl_src.add(putil.get_tbl_cell_lft_pad(f'Name', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad(f"{dataset_info['name']}", padding=0))

        # File format
        tbl_src.add(putil.get_tbl_cell_lft_pad(f'File format', padding=self.indent1))
        tbl_src.add(putil.get_tbl_cell_lft_pad(f"{dataset_info['fileFormat']}", padding=0))

        # Upload date
        tbl_src.add(putil.get_tbl_cell_lft_pad(f'Upload Date', padding=self.indent1))
        date_str = dataset_info['upload_date']['human_readable']
        tbl_src.add(putil.get_tbl_cell_lft_pad(date_str, padding=0))

        # ------------------------------
        # User information
        # ------------------------------
        tbl_src.add(putil.get_tbl_cell_ital("User Information", col_span=2))

        # Name
        tbl_src.add(putil.get_tbl_cell_lft_pad(f'Name', padding=self.indent1))
        name_fmt = '(Not Available)'
        if dataset_info['creator']['first_name'] and dataset_info['creator']['last_name']:
            name_fmt = dataset_info['creator']['first_name'] + ' ' + dataset_info['creator']['last_name']

        tbl_src.add(putil.get_tbl_cell_lft_pad(name_fmt, padding=0))

        # Add borders padding
        self.set_table_borders_padding(tbl_src)

        # Add to overall doc
        self.add_to_layout(tbl_src)

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

        # Dataset is a UserUpload
        if dataset_info['type'] == DataSetInfo.SourceChoices.UserUpload:
            # note = '!Not a Dataverse dataset. Add handling! (pdf_report_maker.py / add_data_source_and_lib)'
            # self.add_to_layout(putil.txt_reg_para(note))
            self.add_dataset_upload_info(dataset_info)
            self.add_opendp_lib_info()
            return

        # Dataset is from Dataverse
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

        dataverse_url = f"{dataset_info['installation']['url']}"
        tbl_src.add(putil.get_tbl_cell_lft_pad(f'URL', padding=self.indent1))
        dv_url_tbl_cell = putil.get_tbl_cell_lft_pad(dataverse_url, padding=0)
        tbl_src.add(dv_url_tbl_cell)

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

        self.set_table_borders_padding(tbl_src)
        self.add_to_layout(tbl_src)

        # Add links
        self.current_page.append_annotation(RemoteGoToAnnotation(
            dv_url_tbl_cell.get_bounding_box(),
            uri=dataverse_url))

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

        # Add PyPI info and reference to add link
        tbl_src.add(putil.get_tbl_cell_lft_pad(f'Python package', padding=self.indent1))
        pypi_tbl_cell = putil.get_tbl_cell_lft_pad(pdf_static.PYPI_OPENDP_URL, padding=0)
        tbl_src.add(pypi_tbl_cell)

        # Add GitHub repo info and reference to add link
        github_repo_url = f"{dp_lib_info['url']}"
        tbl_src.add(putil.get_tbl_cell_lft_pad(f'GitHub Repository', padding=self.indent1))
        github_tbl_cell = putil.get_tbl_cell_lft_pad(github_repo_url, padding=0)
        tbl_src.add(github_tbl_cell)

        self.set_table_borders_padding(tbl_src)

        self.add_to_layout(tbl_src)

        # Add links
        self.current_page.append_annotation(RemoteGoToAnnotation(
            pypi_tbl_cell.get_bounding_box(),
            uri=pdf_static.PYPI_OPENDP_URL))

        self.current_page.append_annotation(RemoteGoToAnnotation(
            github_tbl_cell.get_bounding_box(),
            uri=github_repo_url))

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

        para_read_carefully = ('Please read the report carefully, especially in'
                               ' regard to the usage of these statistics. If you have'
                               ' any questions, please email us info@opendp.org.')

        para_attachment = (f'Note: If you are using Adobe Acrobat, a JSON version of this data'
                           f' is attached to this PDF as a file named'
                           f' "{self.get_embed_json_fname()}."')

        intro_page_paras = [intro_text, para_read_carefully, para_attachment]
        for para_text in intro_page_paras:
            para_obj = putil.txt_reg_para(para_text)
            self.add_to_layout(para_obj)

        self.add_to_layout(Paragraph('Contents',
                                     font=putil.BASIC_FONT_BOLD,
                                     font_size=putil.BASIC_FONT_SIZE,
                                     multiplied_leading=Decimal(1.75)))

        para_section1_obj = putil.txt_list_para(self.SECTION_TITLE_01_STATISTICS)
        self.add_to_layout(para_section1_obj)
        stat_cnt = 0
        predicted_page_num = 1  # assumes stat-specific info starts on page 2

        for stat_info in self.release_dict['statistics']:
            stat_cnt += 1
            stat_type = 'DP ' + stat_info['statistic'].title()
            var_name = stat_info['variable']

            toc_text = f'1.{stat_cnt}. {var_name} - {stat_type}'
            pdf_para_obj = putil.txt_list_para(toc_text,
                                               pdf_static.TOC_L2_LINK_OFFSET)
            self.add_to_layout(pdf_para_obj)

            # for adding links later--when the stats pages exist!
            predicted_page_num += 1

            # add link for "1. Statistics" -- link it to the 1st stat
            if predicted_page_num == 2:
                self.save_intrapage_link(self.SECTION_TITLE_01_STATISTICS,
                                         para_section1_obj,
                                         predicted_page_num, pdf_static.TOC_L1_LINK_OFFSET)

            # add link for sub statistic. 1.1, 1.2, etc.
            #
            self.save_intrapage_link(toc_text, pdf_para_obj, predicted_page_num)
            if stat_info['statistic'] == astatic.DP_HISTOGRAM:
                predicted_page_num += 1  # histograms take two pages

        # Add other TOC links for sections 2 onward
        sections_to_add = [self.SECTION_TITLE_02_DATA_SOURCE,
                           self.SECTION_TITLE_03_OPENDP_LIB,
                           self.SECTION_TITLE_04_USAGE,
                           self.SECTION_TITLE_05_NEGATIVE_VALUES,
                           ]

        for sec_text in sections_to_add:
            pdf_para_obj = putil.txt_list_para(sec_text)
            self.add_to_layout(pdf_para_obj)
            if sec_text != self.SECTION_TITLE_03_OPENDP_LIB:  # Sections 2 and 3 are on the same page
                predicted_page_num += 1
            if sec_text == self.SECTION_TITLE_05_NEGATIVE_VALUES:
                # The previous section takes two pages
                predicted_page_num += 1

            self.save_intrapage_link(sec_text, pdf_para_obj,
                                     predicted_page_num, pdf_static.TOC_L1_LINK_OFFSET)

    def add_intra_page_links(self):
        """
        Add links from the PDF's first page TOC the other pages. TOC example:
            1. Statistics
                1.1. blinkInterval - DP Mean
                1.2. trial - DP Histogram
                1.3. typingSpeed - DP Variance
            2. Data Source
            3. OpenDP Library
            4. Usage / Negative Values
        """
        if self.has_error():
            return

        # Interate through the intra page link info and
        #   add the links within the PDF
        #
        for _txt_to_link, pdf_object, page_num, indent in self.intrapage_link_info:
            """
            _txt_to_link - used for debugging, it's not needed to make the actual PDF link
            pdf_object - the source object to add the link to
            page_num - the destination page when the pdf_object is clicked
            indent - resize the bounding box used for the link source to better fit the text
            """
            pdf_page_idx = Decimal(page_num) - Decimal(1)  # PDF pages within the doc start with 0
            if pdf_page_idx < 0:  # shouldn't happen!
                self.add_err_msg((f'pdf_report_maker. Error adding TOC links.'
                                  f'pdf_page_idx was less than 0 {pdf_page_idx}'))
                return
            bounding_box = pdf_object.get_bounding_box()  # return a Rectangle object which will be  clickable

            # Move the x value and width closer to the text within the pdf_object
            bounding_box.x = bounding_box.x + Decimal(indent)
            bounding_box.width = bounding_box.width - Decimal(indent - 10)

            # Move the y value and height to better align with the pdf_object text
            bounding_box.y = bounding_box.y - Decimal(3)
            bounding_box.height = bounding_box.height + Decimal(8)

            # Add the link to the PDF!
            link_annotation = LinkAnnotation(
                bounding_box,
                page=pdf_page_idx,
                destination_type=DestinationType.FIT,
                color=HexColor("#ffffff"),  # Without this, a black border is placed around the clickable area
            )
            self.first_page.append_annotation(link_annotation)

    @staticmethod
    def get_layout_box(p: Paragraph) -> Rectangle:
        """From https://stackoverflow.com/questions/69318059/create-documents-with-dynamic-height-with-borb"""
        pg: Page = Page()
        zero_dec: Decimal = Decimal(0)
        _width: Decimal = Decimal(1000)  # max width you would allow
        _height: Decimal = Decimal(1000)  # max height you would allow
        return p.layout(pg, Rectangle(zero_dec, zero_dec, _width, _height))

    def format_stat(self, val):
        """Format a numeric statistic. Used to be used for rounding"""
        if val is None:
            return '(not available)'

        # return round(val, 4)  # round to 4 decimal places

        return val

    def add_histogram_result_table(self, stat_info: dict, stat_type: str, var_name: str):
        """
        Add the result table for a single stat, such as DP Mean. Example:
            DP Mean                 2.9442
            Accuracy                0.1964
            Confidence Level        95.0%
            Description             There is a probability of 95.0% that the ... (etc)
        """
        tbl_result = FlexibleColumnWidthTable(number_of_rows=5,
                                              number_of_columns=2,
                                              padding_left=Decimal(40),
                                              padding_right=Decimal(60),
                                              padding_bottom=Decimal(0),
                                              )
        # Statistic name and result
        tbl_result.add(putil.get_tbl_cell_lft_pad(f'DP {stat_type}', padding=0))
        categories = stat_info['result']['value']['categories']
        result_text = (f'The results, in JSON format, may accessed'
                       f' through the PDF attachment "{self.get_embed_json_fname()}"')
        if len(categories) == 1:
            tbl_result.add(putil.get_tbl_cell_lft_pad(f"(1 bin/category). {result_text}", padding=0))
        else:
            tbl_result.add(putil.get_tbl_cell_lft_pad(f"({len(categories)} bins/categories). {result_text}",
                                                      padding=0))

        # Accuracy
        tbl_result.add(putil.get_tbl_cell_lft_pad("Accuracy", padding=0))
        acc_fmt = self.format_stat(stat_info['accuracy']['value'])
        tbl_result.add(putil.get_tbl_cell_align_rt(f"{acc_fmt}"))

        # Confidence Level
        clevel = self.format_stat(stat_info['confidence_level'] * 100.0)
        tbl_result.add(putil.get_tbl_cell_lft_pad("Confidence Level", padding=0))
        tbl_result.add(putil.get_tbl_cell_align_rt(f"{clevel}%"))

        # Noise Mechanism
        tbl_result.add(putil.get_tbl_cell_lft_pad("Noise Mechanism", padding=0))
        noise_mechansim = stat_info['noise_mechanism']
        if not noise_mechansim:
            noise_mechansim = '(not available)'
        tbl_result.add(putil.get_tbl_cell_align_rt(noise_mechansim))

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
        tbl_result = FlexibleColumnWidthTable(number_of_rows=5,
                                              number_of_columns=2,
                                              padding_left=Decimal(40),
                                              padding_right=Decimal(60),
                                              padding_bottom=Decimal(0),
                                              )
        # Statistic name and result
        tbl_result.add(putil.get_tbl_cell_lft_pad(f'DP {stat_type}', padding=0))
        res_fmt = self.format_stat(stat_info['result']['value'])
        tbl_result.add(putil.get_tbl_cell_align_rt(f"{res_fmt}"))

        # Accuracy
        tbl_result.add(putil.get_tbl_cell_lft_pad("Accuracy", padding=0))
        acc_fmt = self.format_stat(stat_info['accuracy']['value'])
        tbl_result.add(putil.get_tbl_cell_align_rt(f"{acc_fmt}"))

        # Confidence Level
        clevel = self.format_stat(stat_info['confidence_level'] * 100.0)
        tbl_result.add(putil.get_tbl_cell_lft_pad("Confidence Level", padding=0))
        tbl_result.add(putil.get_tbl_cell_align_rt(f"{clevel}%"))

        # Noise Mechanism
        tbl_result.add(putil.get_tbl_cell_lft_pad("Noise Mechanism", padding=0))
        noise_mechansim = stat_info['noise_mechanism']
        if not noise_mechansim:
            noise_mechansim = '(not available)'
        tbl_result.add(putil.get_tbl_cell_align_rt(noise_mechansim))

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
        logger.debug('hist_vals', hist_vals)
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
            page.append_annotation(RemoteGoToAnnotation(logo_img_obj.get_bounding_box(),
                                                        uri="https://www.opendp.org"))
