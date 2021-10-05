from pdf_renderer import PDFRenderer


class RenderRelease(object):

    def __init__(self, statistics, histograms):
        self.statistics = statistics
        self.histograms = histograms
        self.renderer = PDFRenderer(self.statistics, self.histograms)
        self.renderer.fill_document()

    def read_latex(self):
        return self.renderer.get_latex()

    def save_latex(self, filepath):
        self.renderer.save_latex(filepath)

    def save_pdf(self, filepath):
        self.renderer.save_pdf(filepath)