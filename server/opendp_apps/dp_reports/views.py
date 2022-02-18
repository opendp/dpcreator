import json
from .forms import ReportForm
from .pdf_report_maker import PDFReportMaker

from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def view_create_pdf_report(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ReportForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            json_release = form.cleaned_data['json_release']

            pdf_maker = PDFReportMaker(json_release)
            if not pdf_maker.has_error():
                pass

            retrieved, pdf_contents_or_err = pdf_maker.get_pdf_contents()
            if not retrieved:
                return HttpResponse(f'Error: {pdf_contents_or_err}')

            response = HttpResponse(pdf_contents_or_err,
                                    content_type='application/pdf')
            #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
            return response

    else:
        form = ReportForm()

    info_dict = dict(form=form)

    return render(request,
                  'pdf_report/view_create_pdf_report.html',
                  info_dict)