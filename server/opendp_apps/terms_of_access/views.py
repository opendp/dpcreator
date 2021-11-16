from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions

from opendp_apps.terms_of_access.models import TermsOfAccessLog, TermsOfAccess
from opendp_apps.terms_of_access.serializers import TermsOfAccessSerializer, TermsOfAccessLogSerializer
from opendp_project.views import BaseModelViewSet


class TermsOfAccessViewSet(BaseModelViewSet):
    queryset = TermsOfAccess.objects.all().order_by('-created')
    serializer_class = TermsOfAccessSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get']


class TermsOfAccessAgreementViewSet(BaseModelViewSet):
    queryset = TermsOfAccessLog.objects.all().order_by('-created')
    serializer_class = TermsOfAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]
