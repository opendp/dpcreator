from rest_framework import viewsets, permissions

from opendp_apps.user.models import OpenDPUser #Session
from opendp_apps.user.serializers import UserSerializer # SessionSerializer,


"""
class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
"""


class UserViewSet(viewsets.ModelViewSet):
    """
    view/edit users
    """
    queryset = OpenDPUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
