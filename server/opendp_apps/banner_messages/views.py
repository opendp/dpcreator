from django.utils import timezone

from rest_framework import permissions, viewsets

from opendp_apps.banner_messages.models import BannerMessage
from opendp_apps.banner_messages.serializers import BannerMessageSerializer
from opendp_project.views import BaseModelViewSet


class BannerMessageViewSet(viewsets.ModelViewSet):
    """Viewset for Banner Messages"""
    lookup_field = 'object_id'

    serializer_class = BannerMessageSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get']

    def get_queryset(self):
        """
        View active BannerMessage objects
        """
        return BannerMessage.get_active_banners()
