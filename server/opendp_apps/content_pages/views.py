from django.shortcuts import render
from django.http import HttpResponse


def view_opendp_welcome(request):
    """home page"""
    dinfo = dict(title='OpenDP App..',
                 description='Test Differential Privacy')

    return render(request,
                  'content_pages/index.html',
                  dinfo)
