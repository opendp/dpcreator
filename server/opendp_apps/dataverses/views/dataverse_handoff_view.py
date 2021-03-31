from rest_framework import viewsets, status
from rest_framework.response import Response

from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.serializers import DataverseHandoffSerializer
from opendp_apps.utils.view_helper import get_json_error


class DataverseHandoffView(viewsets.ViewSet):

    def get_serializer(self, instance=None):
        return DataverseHandoffSerializer()

    def list(self, request):
        queryset = DataverseHandoff.objects.all()
        serializer = DataverseHandoffSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        """Temporarily save the Dataverse paramemeters +
        redirect to the Vue page"""
        # create a form instance and populate it with data from the request:
        dataverse_handoff = DataverseHandoffSerializer(data=request.data)

        # check whether it's valid:
        if dataverse_handoff.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            new_obj = dataverse_handoff.save()
            # would redirect to Vue page here!!!

            # TODO: 'vue-home' isn't defined so this endpoint breaks
            # client_url = reverse('vue-home') + f'?id={str(new_obj.object_id)}'
            # print('client_url', client_url)
            return Response({'id': new_obj.object_id}, status=status.HTTP_201_CREATED)
            # return HttpResponseRedirect(client_url)

            # return JsonResponse(dict(message='ok',
            #                          uuid=str(new_obj.object_id)))

        # if a GET (or any other method) we'll create a blank form
        else:
            return Response(get_json_error(dataverse_handoff.errors), status=status.HTTP_400_BAD_REQUEST)
