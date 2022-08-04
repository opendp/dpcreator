from django.urls import path

from opendp_apps.dp_reports import views

urlpatterns = [
    path('make-pdf', views.view_create_pdf_report, name='view_create_pdf_report'),
]
