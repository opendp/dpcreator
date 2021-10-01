class LatexRequestFormatter(object):

    def __init__(self, release):
        """
        Format a Release object to be sent to the LaTeX microservice
        :param release:
        """
        self.release = release

    def format(self):
        statistics = dict((x['statistic'], x['result']['value'],) for x in self.release.dp_release['statistics'])
        return {
            'statistics': statistics,
            'histograms': self.release.dp_release['histograms'],
            'object_id': str(self.release.object_id),
            'base_filename': '-'.join(['release', str(self.release.object_id)])
        }



