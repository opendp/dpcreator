from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import DataverseUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataverseUser
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
