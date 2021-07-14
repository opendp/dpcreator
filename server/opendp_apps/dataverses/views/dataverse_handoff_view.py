from django.http import HttpResponseRedirect
from django.urls import reverse

from requests.utils import quote

from rest_framework.response import Response
from rest_framework.decorators import action

from opendp_apps.dataverses.models import DataverseHandoff, RegisteredDataverse
from opendp_apps.dataverses.serializers import DataverseHandoffSerializer
from opendp_apps.dataverses import static_vals as dv_static
from opendp_project.views import BaseModelViewSet


class DataverseHandoffView(BaseModelViewSet):

    queryset = DataverseHandoff.objects.all()
    serializer_class = DataverseHandoffSerializer

    # This needs to be available before login
    permission_classes = []

    def list(self, request, *args, **kwargs):
        queryset = DataverseHandoff.objects.all()
        serializer = DataverseHandoffSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def dv_orig_create(self, request):
        """Access Create via a GET. This is temporary until the Dataverse signed urls are available"""
        print('--- createbyget ---')
        request_data = request.query_params.copy()
        return self.process_dataverse_data(request_data)

        #return Response({"From Hello": "Got it"})

    def create(self, request, *args, **kwargs):
        """
        Temporarily save the Dataverse paramemeters +
        redirect to the Vue page
        """
        print('--- create! ---')
        request_data = request.data.copy()
        return self.process_dataverse_data(request_data)


    def process_dataverse_data(self, request_data):
        """Process incoming Dataverse data
        - Used by both the GET and POST endpoints
        """
        print('--- process_dataverse_data ---')

        if dv_static.DV_PARAM_SITE_URL in request_data:
            init_site_url = request_data[dv_static.DV_PARAM_SITE_URL]
            request_data[dv_static.DV_PARAM_SITE_URL] = RegisteredDataverse.format_dv_url(init_site_url)

        handoff_serializer = DataverseHandoffSerializer(data=request_data)

        if handoff_serializer.is_valid():

            new_dv_handoff = handoff_serializer.save()
            new_dv_handoff.save()

            client_url = reverse('vue-home') + f'?id={str(new_dv_handoff.object_id)}'
            # return Response({'id': new_obj.object_id}, status=status.HTTP_201_CREATED)
            return HttpResponseRedirect(client_url)
        else:
            error_code = ''
            for k, v in handoff_serializer.errors.items():
                for error_detail in v:
                    #if error_detail.code in ['does_not_exist', 'required'] and k is not None:
                    if error_detail.code and k is not None:
                        error_code += ','.join([k, ''])
            # Remove trailing comma
            error_code = quote(error_code[:-1])
            print('error_code', error_code)
            return HttpResponseRedirect(reverse('vue-home') + f'?error_code={error_code}')
