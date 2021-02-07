from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView


#router.register(r'updatetime', views.UpdateTimeViewSet, base_name='updatetime')

class UpdateTimeView(APIView):

    def get(self, request, format=None):

        return Response({
            "publish_updatetime": datetime.now(),
        })