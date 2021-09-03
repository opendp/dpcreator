from rest_framework import serializers

from opendp_apps.terms_of_access.models import TermsOfAccess, TermsOfAccessLog
from opendp_apps.user.models import OpenDPUser


class TermsOfAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsOfAccess
        fields = ['object_id', 'name', 'active', 'description', 'version', 'notes', 'created']


class TermsOfAccessLogSerializer(serializers.ModelSerializer):
    terms_of_access = serializers.SlugRelatedField(queryset=TermsOfAccess.objects.all(),
                                                   slug_field='object_id',
                                                   read_only=False)
    user = serializers.SlugRelatedField(queryset=OpenDPUser.objects.all(),
                                        slug_field='object_id',
                                        read_only=False)

    class Meta:
        model = TermsOfAccessLog
        fields = ['user', 'terms_of_access']
