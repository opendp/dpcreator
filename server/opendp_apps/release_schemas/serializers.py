from rest_framework import serializers

from opendp_apps.release_schemas.models import ReleaseInfoSchema


class ReleaseSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReleaseInfoSchema
        fields = ['schema']
        read_only_fields = ['schema']

    def to_representation(self, value):
        return value.schema
