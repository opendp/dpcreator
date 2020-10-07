from django.contrib.auth.models import Group
from rest_framework import permissions, viewsets
from .serializers import UserSerializer, GroupSerializer, SessionSerializer
from .models import DataverseUser, Session


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    view/edit users
    """
    queryset = DataverseUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    view/edit groups
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

