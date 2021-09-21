from opendp_apps.results.tools.pdf_renderer import PDFRenderer


class RenderRelease(object):

    def __init__(self, release):
        self.release = release
        self.statistics = [(x['statistic'], x['result']['value'],) for x in self.release.dp_release['statistics']]
        self.histograms = []
        self.renderer = PDFRenderer(self.statistics, self.histograms)
        self.renderer.fill_document()

    def read_latex(self):
        return self.renderer.get_latex()

    def save_latex(self, filepath):
        self.renderer.save_latex(filepath)