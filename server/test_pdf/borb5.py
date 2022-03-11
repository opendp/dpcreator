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


def get_layout_box(self, p: Paragraph) -> Rectangle:
    pg: Page = Page()
    ZERO: Decimal = Decimal(0)
    W: Decimal = Decimal(1000)  # max width you would allow
    H: Decimal = Decimal(1000)  # max height you would allow
    return p.layout(pg, Rectangle(ZERO, ZERO, W, H))

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

    num_rows = 46
    table_001 = FlexibleColumnWidthTable(number_of_rows=num_rows,
                                         number_of_columns=2,
                                         padding_left=Decimal(40),
                                         padding_right=Decimal(40))
    table_001.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))
    table_001.set_border_color_on_all_cells(HexColor('006699'))
    table_001.set_borders_on_all_cells(True, False, True, False)  # top, right, left, bottom

    table_001.add(TableCell(Paragraph("Privacy Parameters"), col_span=2))
    for cnt in range(1, num_rows):

        table_001.add(TableCell(Paragraph(f"{cnt}"), col_span=2))

    test_rect = get_layout_box(table_001)
    print('test_rect w x h', test_rect.width, test_rect.height)

    #print(dir(table_001.get_bounding_box().__sizeof__))
    #print(table_001.get_bounding_box().__sizeof__())
    try:
        layout.add(table_001)
    except AssertionError as ex_obj:
        print(ex_obj)
        if str(ex_obj) == 'AssertionError: FlexibleColumnWidthTable is too tall to fit inside column / page.':
            print('AssertionError 1')
        elif str(ex_obj) == 'A Rectangle must have a non-negative height.':
            print('AssertionError 2')

        try:
            next_page: Page = Page()
            doc.append_page(next_page)
            layout: PageLayout = SingleColumnLayout(next_page)
            layout.add(table_001)
        except AssertionError as ex_obj:
            print(ex_obj)
            print('uh oh! This element does not work!')

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