from django.http import HttpResponseRedirect
from django.urls import reverse
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
            return HttpResponseRedirect(reverse('vue-home'))
