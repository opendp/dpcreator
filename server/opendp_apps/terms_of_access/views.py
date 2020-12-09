from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from rest_framework.views import APIView

from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.terms_of_access.models import TermsOfAccessLog, TermsOfAccess
from opendp_apps.terms_of_access.serializers import TermsOfAccessSerializer, TermsOfAccessLogSerializer


class TermsOfAccessViewSet(viewsets.ModelViewSet):
    """
    view/edit users
    """
    queryset = TermsOfAccess.objects.all().order_by('-created')
    serializer_class = TermsOfAccessSerializer
    permission_classes = [permissions.IsAuthenticated]


class TermsOfAccessAgreementViewSet(viewsets.ModelViewSet):
    queryset = TermsOfAccessLog.objects.all().order_by('-created')
    serializer_class = TermsOfAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]


class TermsOfAccessAgreement(APIView):

    def post(self, request, *args, **kwargs):
        print(kwargs)
        datasetinfo = DataSetInfo.objects.get(id=kwargs.get('dataset_info_id'))
        terms_of_access = TermsOfAccess.objects.get(id=kwargs.get('terms_of_access_id'))
        print(datasetinfo, terms_of_access)
        agreement = TermsOfAccessLog.objects.create(
            user=request.user,
            dataset_info=datasetinfo,
            terms_of_access=terms_of_access)
        return JsonResponse({})
