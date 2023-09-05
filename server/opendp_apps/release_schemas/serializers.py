

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta
from rest_polymorphic.serializers import PolymorphicSerializer

from opendp_apps.release_schemas.models import ReleaseInfoSchema

class ReleaseSchemaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReleaseInfoSchema
        fields = ['name',
                  'version',
                  'is_published',
                  'schema',
                  'description',
                  'schema_link',
                  'id_link',
                  'sortable_version']

        read_only_fields = ['name',
                            'version',
                            'is_published',
                            'schema',
                            'description',
                            'schema_link',
                            'id_link',
                            'sortable_version']
