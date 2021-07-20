from rest_framework import serializers

from opendp_apps.terms_of_access.models import TermsOfAccess, TermsOfAccessLog


class TermsOfAccessSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TermsOfAccess
        fields = ['object_id', 'name', 'active', 'description', 'version', 'notes', 'created']


class TermsOfAccessLogSerializer(serializers.HyperlinkedModelSerializer):
    terms_of_access = TermsOfAccessSerializer(read_only=True)

    class Meta:
        model = TermsOfAccessLog
        fields = ['user', 'terms_of_access']
