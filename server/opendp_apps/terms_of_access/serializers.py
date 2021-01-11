from rest_framework import serializers

from opendp_apps.terms_of_access.models import TermsOfAccess, TermsOfAccessLog


class TermsOfAccessSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TermsOfAccess
        fields = ['name', 'active', 'description', 'version', 'notes']


class TermsOfAccessLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TermsOfAccessLog
        fields = ['user', 'dataset_info', 'terms_of_access']
