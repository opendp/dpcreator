from decimal import Decimal
import os

from borb.pdf.canvas.color.color import X11Color
from borb.pdf.canvas.geometry.rectangle import Rectangle
from borb.pdf.canvas.layout.shape.shape import Shape
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.canvas.line_art.line_art_factory import LineArtFactory
from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from borb.pdf.canvas.color.color import HSVColor, HexColor, Color
from borb.pdf.canvas.layout.table.flexible_column_width_table import FlexibleColumnWidthTable
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.layout.text.paragraph import Paragraph



def main():
    doc: Document = Document()
    page: Page = Page()
    doc.append_page(page)

    layout: PageLayout = SingleColumnLayout(page)

    print('layout._page_width 1', layout._page_width)
    print('layout._page_height 1', layout._page_height)


    r: Rectangle = Rectangle(Decimal(0),
                             Decimal(0),
                             Decimal(400),
                             Decimal(100))
    layout.add(Shape(LineArtFactory.sticky_note(r),
                     stroke_color=X11Color("Blue"),
                     fill_color=X11Color("White"),
                     line_width=Decimal(1)
                     ))

    table_001 = FlexibleColumnWidthTable(number_of_rows=5,
                                         number_of_columns=2,
                                         padding_left=Decimal(40),
                                         padding_right=Decimal(40),
                                         border_color=HexColor('006699'))

    table_001.add(TableCell(Paragraph("Privacy Parameters"), col_span=2))
    print(dir(table_001.get_bounding_box().__sizeof__))
    print(table_001.get_bounding_box().__sizeof__())
    layout.add(table_001)

    print('layout._page_width 2 ', layout._page_width)
    print('layout._page_height 2', layout._page_height)

    pdf_fname = "output.pdf"
    with open(pdf_fname, "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, doc)

    os.system(f'open {pdf_fname}')

def get_layout_box(p: Paragraph) -> Rectangle:
    pg: Page = Page()
    ZERO: Decimal = Decimal(0)
    W: Decimal = Decimal(1000)   # max width you would allow
    H: Decimal = Decimal(1000)   # max height you would allow
    return p.layout(pg, Rectangle(ZERO, ZERO, W, H))

if __name__ == "__main__":
    main()