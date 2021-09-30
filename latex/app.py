import json
import os

import web

from pdf_renderer import PDFRenderer

urls = (
    '/', 'hello'
)
app = web.application(urls, globals())


class hello:
    def GET(self, name):
        if not name:
            name = 'World'
        return 'Hello, ' + name + '!'

    def POST(self):
        """
        This would take JSON with stats / histograms, build the PDF, and
        save it to S3, etc. Then return a JSON response with the S3 key
        that the server can use to download the rendered file (or show to the frontend to download)
        e.g.
        {
          "statistics": {
            "mean": 3.14,
            "count": 10
          },
          "histograms": {
            "test": {
              "data": [1, 2, 3, 4, 5],
              "height": [1,2,3,4,5]
            }
          },
          "object_id": 1234,
          "base_filename": "test_file"
        }
        :return:
        """
        local_output_dir = 'output'
        azure_root = 'dp_creator_pdfs'

        data = json.loads(web.data())
        stats = data.get('statistics', {})
        hists = data.get('histograms', {})
        object_id = data.get('object_id')
        if stats == {} and hists == {}:
            raise web.badrequest({'error': 'One of \'statistics\' and \'histograms\' must be given'})

        base_filename = os.path.join(local_output_dir, data.get('base_filename'))
        pdf_renderer = PDFRenderer(stats, hists)
        pdf_renderer.save_pdf(base_filename)
        return {'key': os.path.join(azure_root, base_filename + '.pdf'), 'object_id': object_id}


if __name__ == "__main__":
    app.run()
