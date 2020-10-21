from django.shortcuts import render
from rest_framework import viewsets, permissions

from opendp_apps.user.models import Session, DataverseUser
from opendp_apps.user.serializers import SessionSerializer, UserSerializer


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