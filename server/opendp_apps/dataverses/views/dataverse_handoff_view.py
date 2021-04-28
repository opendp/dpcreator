from django.http import HttpResponseRedirect
from django.urls import reverse
from requests.utils import quote
from rest_framework import viewsets
from rest_framework.response import Response

from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.serializers import DataverseHandoffSerializer


class DataverseHandoffView(viewsets.ViewSet):

    def get_serializer(self, instance=None):
        return DataverseHandoffSerializer()

    def list(self, request):
        queryset = DataverseHandoff.objects.all()
        serializer = DataverseHandoffSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        """
        Temporarily save the Dataverse paramemeters +
        redirect to the Vue page
        """
        ## Fix this!!! #161
        request_data = request.data.copy()
        print('handoff-create: request.data', request_data)

        dataverse_handoff = DataverseHandoffSerializer(data=request_data)

        if dataverse_handoff.is_valid():

            new_dv_handoff = dataverse_handoff.save()
            # serious hack
            ## Fix this!!! #161
            new_dv_handoff.siteUrl = new_dv_handoff.dv_installation.dataverse_url

            if 'token' in request_data:
                new_dv_handoff.apiGeneralToken = request_data['token']
            if 'fileId' in request_data:
                new_dv_handoff.fileId = request_data['fileId']

            new_dv_handoff.save()

            # Fix this!!! #161
            if not new_dv_handoff.is_site_url_registered():
                error_code = 'site_url'
                return HttpResponseRedirect(reverse('vue-home') + f'?error_code={error_code}')

            client_url = reverse('vue-home') + f'?id={str(new_dv_handoff.object_id)}'
            # return Response({'id': new_obj.object_id}, status=status.HTTP_201_CREATED)
            return HttpResponseRedirect(client_url)
        else:
            error_code = ''
            for k, v in dataverse_handoff.errors.items():
                for error_detail in v:
                    if error_detail.code in ['does_not_exist', 'required'] and k is not None:
                        error_code += ','.join([k, ''])
            # Remove trailing comma
            error_code = quote(error_code[:-1])
            print('error_code', error_code)
            return HttpResponseRedirect(reverse('vue-home') + f'?error_code={error_code}')
