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

        dataverse_handoff = DataverseHandoffSerializer(data=request.data)

        if dataverse_handoff.is_valid():
            new_obj = dataverse_handoff.save()
            client_url = reverse('vue-home') + f'?id={str(new_obj.object_id)}'
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
            return HttpResponseRedirect(reverse('vue-home') + f'?error_code={error_code}')
