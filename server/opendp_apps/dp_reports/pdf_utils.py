"""
Used for making the Release PDF
"""
from decimal import Decimal
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.text.chunk_of_text import ChunkOfText
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.color.color import HexColor

from opendp_apps.dp_reports import font_util

COLOR_CRIMSON = HexColor('#a41d30')
BASIC_FONT = font_util.get_custom_font(font_util.OPEN_SANS_LIGHT)
BASIC_FONT_ITALIC = font_util.get_custom_font(font_util.OPEN_SANS_ITALIC)
BASIC_FONT_BOLD = font_util.get_custom_font(font_util.OPEN_SANS_SEMI_BOLD)

BASIC_FONT_SIZE = Decimal(9)
SUBTITLE_FONT_SIZE = BASIC_FONT_SIZE + Decimal(1)
TBL_FONT_SIZE = Decimal(9)
TBL_BORDER_COLOR = HexColor("#cbcbcb")


def get_centered_para(s):
    """Add a paragraph to the layout"""
    p = Paragraph(s,
                  font=font_util.get_custom_font(font_util.OPEN_SANS_SEMI_BOLD),
                  font_size=Decimal(10),
                  font_color=COLOR_CRIMSON,
                  multiplied_leading=Decimal(1.25),
                  respect_newlines_in_text=True,
                  text_alignment=Alignment.CENTERED)
    return p


def get_tbl_cell_ital(content, col_span=1, padding=0):
    """Get table cell, putting the content in italics"""
    return _get_tbl_cell(content,
                         BASIC_FONT_ITALIC,
                         TBL_FONT_SIZE,
                         Alignment.LEFT,
                         col_span=col_span,
                         padding_left=padding)


def get_tbl_cell_lft_pad(content, padding=10):
    """Return a table cell aligned left with left padding"""
    return _get_tbl_cell(content,
                         BASIC_FONT,
                         TBL_FONT_SIZE,
                         Alignment.LEFT,
                         col_span=1,
                         padding_left=padding)


def get_tbl_cell_align_rt(content):
    """Return a table cell aligned right"""
    return _get_tbl_cell(content, BASIC_FONT, TBL_FONT_SIZE, Alignment.RIGHT)


def _get_tbl_cell(content, font=None, font_size=None, text_alignment=None,
                  col_span=1, padding_left=0) -> TableCell:
    """Return a Paragraph within a TableCell"""
    if not font:
        font = BASIC_FONT
    if not font_size:
        font = BASIC_FONT_SIZE
    if not text_alignment:
        text_alignment = Alignment.LEFT

    p = Paragraph(content,
                  font=font,
                  font_size=font_size,
                  padding_left=Decimal(padding_left),
                  text_alignment=text_alignment)
    return TableCell(p,
                     # border_color=TBL_BORDER_COLOR,
                     col_span=col_span)


def txt_reg(val):
    """Return a chunk of text with a regular font"""
    return ChunkOfText(val, font=BASIC_FONT, font_size=BASIC_FONT_SIZE)


def txt_subtitle_para(subtitle):
    """Return a Paragraph with a subtitle font"""
    return Paragraph(subtitle,
                     font=BASIC_FONT_BOLD,
                     font_size=SUBTITLE_FONT_SIZE,
                     font_color=COLOR_CRIMSON,
                     multiplied_leading=Decimal(1.75))

def txt_reg_para_pl40(val):
    """Create a paragraph with a left padding of 40"""
    return txt_reg_para(val, padding_left=Decimal(40))

def txt_reg_para(val, padding_left=Decimal(0)):
    """Return a Paragraph with a regular font"""
    return Paragraph(val,
                     font=BASIC_FONT,
                     font_size=BASIC_FONT_SIZE,
                     multiplied_leading=Decimal(1.75),
                     padding_left=padding_left,
                     )


def txt_list_para(val, padding_left=Decimal(40)):
    """Return a paragraph for a listt"""
    return Paragraph(val,
                     # font=BASIC_FONT,
                     font=BASIC_FONT_BOLD,
                     font_size=BASIC_FONT_SIZE,
                     font_color=COLOR_CRIMSON,
                     padding_left=padding_left,
                     padding_bottom=Decimal(0),
                     padding_top=Decimal(0),
                     margin_top=Decimal(0),
                     margin_bottom=Decimal(0),
                     multiplied_leading=Decimal(.5))


def txt_bld(val):
    """Return a chunk of text with a bold font"""
    return ChunkOfText(val, font=BASIC_FONT_BOLD, font_size=BASIC_FONT_SIZE)


def txt_bld_para(val, padding_left=Decimal(0)):
    """Return a chunk of text with a bold font"""
    return Paragraph(val,
                     font=BASIC_FONT_BOLD,
                     font_size=BASIC_FONT_SIZE,
                     padding_left=padding_left,
                     )


def txt_ital_para(val, padding_left=Decimal(0)):
    """Return a chunk of text with a bold font"""
    return Paragraph(val,
                     font=BASIC_FONT_ITALIC,
                     font_size=BASIC_FONT_SIZE,
                     padding_left=padding_left,
                     )
