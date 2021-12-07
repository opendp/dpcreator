from django.utils import timezone

from django.db.models import Q
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
        current_time = timezone.now()

        print('current_time', current_time)

        # Choose Banner Meessages that are active
        #  or active and "timed"
        #
        qs = BannerMessage.objects.filter(
                        Q(active=True, is_timed_message=False) |
                        Q(active=True, is_timed_message=True,
                          view_start_time__lte=current_time,
                          view_stop_time__gte=current_time)\
                        ).order_by('active', 'sort_order', '-created')

        return qs