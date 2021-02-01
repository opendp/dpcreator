from rest_framework import viewsets, permissions

from opendp_apps.user.models import OpenDPUser #Session
from opendp_apps.user.serializers import UserSerializer # SessionSerializer,
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


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



class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client