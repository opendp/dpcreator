from rest_framework import viewsets, permissions

from opendp_apps.user.models import OpenDPUser  # Session
from opendp_apps.user.serializers import OpenDPUserSerializer  # SessionSerializer,
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.registration.views import RegisterView

from opendp_project.views import BaseModelViewSet

"""
class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
"""


class UserViewSet(BaseModelViewSet):
    """
    view/edit users
    """
    queryset = OpenDPUser.objects.all().order_by('-date_joined')
    serializer_class = OpenDPUserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


class OpenDPRegister(RegisterView):
    """
    Override default behavior,
    which doesn't return user info when email verification is mandatory
    """

    def get_response_data(self, user):
        return {user.object_id}
