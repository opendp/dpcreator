from decimal import Decimal
import os

from borb.pdf.canvas.geometry.rectangle import Rectangle
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF


def main():
    doc: Document = Document()
    page: Page = Page()
    doc.append_page(page)

    p: Paragraph = Paragraph("Hello World!")

    # the next line of code uses absolute positioning
    r: Rectangle = Rectangle(Decimal(59),  # x: 0 + page_margin
                             Decimal(848 - 84 - 100),  # y: page_height - page_margin - height_of_textbox
                             Decimal(595 - 59 * 2),  # width: page_width - 2 * page_margin
                             Decimal(100))  # height
    p.layout(page, r)

    # write
    pdf_fname = "output.pdf"
    with open(pdf_fname, "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, doc)

    os.system(f'open {pdf_fname}')

if __name__ == "__main__":
    main()


