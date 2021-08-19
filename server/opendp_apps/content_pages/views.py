from django.shortcuts import render
from django.http import HttpResponse


def view_opendp_welcome(request):
    """home page"""
    dinfo = dict(title='DP Creator',
                 description='Create differentially private statistics using OpenDP')

    return render(request,
                  'content_pages/index.html',
                  dinfo)
