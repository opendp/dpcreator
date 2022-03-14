import os
from pathlib import Path

from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.pdf import PDF
from borb.pdf.canvas.color.color import HexColor


def main():
    doc: Document = Document()
    page: Page = Page()
    doc.append_page(page)
    layout: PageLayout = SingleColumnLayout(page)

    # construct the Font object
    #font_path: Path = Path(__file__).parent / "Jsfont-Regular.ttf"
    #font: Font = TrueTypeFont.true_type_font_from_file(font_path)

    layout.add(Paragraph("Hello World!"))
    layout.add(Paragraph("Hello World!",
                         font="Times-roman",
                         font_color=HexColor("#86CD82")))

    pdf_fname = "output.pdf"
    with open(pdf_fname, "wb") as out_file_handle:
        PDF.dumps(out_file_handle, doc)

    os.system(f'open {pdf_fname}')

if __name__ == "__main__":
    main()


"""
from borb.pdf.page.page_size import PageSize
"""