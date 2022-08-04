from rest_framework import serializers

from opendp_apps.banner_messages.models import BannerMessage


class BannerMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerMessage
        fields = ['name', 'type', 'content', 'sort_order', 'created', 'object_id', ]
