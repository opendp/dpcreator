import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from requests.utils import quote
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from opendp_apps.utils.view_helper import get_json_error, get_json_success

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import DataverseHandoff, RegisteredDataverse
from opendp_apps.dataverses.serializers import DataverseHandoffSerializer
from opendp_project.views import BaseModelViewSet
from opendp_apps.dataverses.signed_url_handler import SignedUrlHandler

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DataverseHandoffView(BaseModelViewSet):
    queryset = DataverseHandoff.objects.all()
    serializer_class = DataverseHandoffSerializer

    # This needs to be available before login
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """Not allowed"""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        """Not allowed"""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        # queryset = DataverseHandoff.objects.all()
        # serializer = DataverseHandoffSerializer(queryset, many=True, context={'request': request})
        # return Response(serializer.data)

    @action(methods=['post'], detail=False, url_path='init-connection', url_name='init-connection')
    def init_connection(self, request):
        """
        Initialize the Dataverse connection by receiving/validating signed-urls from Dataverse
        """
        request_data = request.data.copy()

        print('request_data', request_data)

        validation_info = SignedUrlHandler.validate_signed_urls(request_data)
        if validation_info.success:
            return Response(get_json_success('The signed urls are valid'), status=status.HTTP_200_OK)
        else:
            return Response(get_json_error(validation_info.message),
                            status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['get', 'post'], detail=False)
    def dv_orig_create(self, request):
        """
        Access Create via a GET. This is temporary and insecure.
        Exists until the Dataverse signed urls are available.
        """
        if request.method == 'POST':
            request_data = request.data.copy()
            for k, v in request.META.items():
                if k.lower().find('signed') > -1:
                    logger.info(f'header key containing "signed": {k}={v}')
        else:
            request_data = request.query_params.copy()

        logger.info('request_data: %s', request_data)

        return self.process_dataverse_data(request_data)

        # return Response({"From Hello": "Got it"})

    def create(self, request, *args, **kwargs):
        """
        Temporarily save the Dataverse paramemeters +
        redirect to the Vue page
        """
        request_data = request.data.copy()
        logger.info(request_data)
        return self.process_dataverse_data(request_data)

    def process_dataverse_data(self, request_data):
        """Process incoming Dataverse data
        - Used by both the GET and POST endpoints
        """
        if dv_static.DV_PARAM_SITE_URL in request_data:
            init_site_url = request_data[dv_static.DV_PARAM_SITE_URL]
            init_site_url = RegisteredDataverse.hack_format_dv_url_http(init_site_url)
            request_data[dv_static.DV_PARAM_SITE_URL] = RegisteredDataverse.format_dv_url(init_site_url)

        # used for error handling
        reg_dv_site_url = None
        if dv_static.DV_PARAM_SITE_URL in request_data:
            reg_dv_site_url = request_data[dv_static.DV_PARAM_SITE_URL]

        handoff_serializer = DataverseHandoffSerializer(data=request_data)

        if handoff_serializer.is_valid():

            new_dv_handoff = handoff_serializer.save()
            new_dv_handoff.save()

            client_url = reverse('vue-home') + f'?id={str(new_dv_handoff.object_id)}'
            logger.info(f'DataverseHandoff successfully saved. Redirecting to {client_url}')
            return HttpResponseRedirect(client_url)
        else:
            logger.info('handoff_serializer.errors: %s', handoff_serializer.errors.items())
            error_code = ''
            for k, v in handoff_serializer.errors.items():
                for error_detail in v:
                    # if error_detail.code in ['does_not_exist', 'required'] and k is not None:
                    if error_detail.code and k is not None:
                        error_code += ','.join([k, ''])
            # Remove trailing comma
            error_code = quote(error_code[:-1])

            logger.error(f'Invalid DataverseHandoffSerializer. Error_code: {error_code}')

            get_str = f'?error_code={error_code}'
            if error_code == dv_static.DV_PARAM_SITE_URL:
                logger.error(f'Not a Registered Dataverse: {reg_dv_site_url}')
                get_str = f'{get_str}&unreg_dv_url={reg_dv_site_url}'

            return HttpResponseRedirect(reverse('vue-home') + get_str)
