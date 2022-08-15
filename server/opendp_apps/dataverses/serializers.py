from datetime import datetime
from urllib import parse

from rest_framework import serializers

from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import RegisteredDataverse, DataverseHandoff
from opendp_apps.user.models import DataverseUser, OpenDPUser


class RegisteredDataverseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisteredDataverse
        fields = ['name', 'dataverse_url',
                  'object_id', 'active',
                  'created', 'updated']


class DataverseUserSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=OpenDPUser.objects.all(),
                                        slug_field='object_id',
                                        read_only=False)
    dv_handoff = serializers.SlugRelatedField(queryset=DataverseHandoff.objects.all(),
                                              slug_field='object_id',
                                              read_only=False)

    # This will mean that the form at http://localhost:8000/api/dv-user/ will only have those three fields,
    class Meta:
        model = DataverseUser
        fields = ['object_id', 'user', 'dv_handoff']

    def save(self, **kwargs):
        dataverse_handoff = self.validated_data.pop('dv_handoff')
        self.validated_data['dv_installation'] = dataverse_handoff.dv_installation
        self.validated_data['dv_general_token'] = dataverse_handoff.apiGeneralToken
        return super().save()

    def update(self, instance, validated_data):
        opendp_user = OpenDPUser.objects.get(object_id=validated_data.get('user'))
        instance.email = opendp_user.email
        instance.first_name = opendp_user.first_name
        instance.last_name = opendp_user.last_name
        # instance.dv_general_token = validated_data.get('dv_general_token')
        # instance.dv_sensitive_token = validated_data.get('dv_sensitive_token')
        # instance.dv_token_update = validated_data.get('dv_token_update')
        instance.save()
        return instance


class DataverseHandoffSerializer(serializers.ModelSerializer):
    # map 'site_url' -> 'dataverse_url'
    site_url = serializers.SlugRelatedField(queryset=RegisteredDataverse.objects.filter(active=True),
                                            slug_field='dataverse_url',
                                            read_only=False,
                                            source='dv_installation')

    class Meta:
        model = DataverseHandoff
        exclude = ['dv_installation']


class DataverseFileInfoMakerSerializer(serializers.ModelSerializer):
    dv_installation = serializers.PrimaryKeyRelatedField(queryset=RegisteredDataverse.objects.all())
    creator = serializers.PrimaryKeyRelatedField(queryset=OpenDPUser.objects.all())

    class Meta:
        model = DataverseFileInfo
        exclude = ['data_profile', 'source_file', 'polymorphic_ctype']


class SingleSignedUrlSerializer(serializers.Serializer):
    """
    Used to validate
    """
    until = serializers.CharField(max_length=30,
                                  help_text='Date/time string. Example: "2022-08-08T11:18:28.368"')
    user = serializers.CharField(max_length=100)
    method = serializers.ChoiceField(choices=dv_static.HTTP_METHOD_CHOICES)
    token = serializers.CharField(max_length=200)

    def validate_until(self, value: str) -> str:
        """
        Check that "until" is a valid datetime
        @param value:
        @return:
        """
        try:
            dt_obj = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')

            # Has the date/time expired?
            if datetime.now() > dt_obj:
                user_msg = f'The date/time, "{value}", for this url has expired.'
                raise serializers.ValidationError(user_msg)

        except ValueError:
            user_msg = dv_static.ERR_MSG_BAD_DATETIME_STRING
            raise serializers.ValidationError(user_msg)

        return value

    def get_errors_in_oneline(self) -> str:
        """
        Combine errors into single line
        @return:
        """
        assert self.is_valid() is False, "Check that is_valid() is False before using this method."

        err_lines = []
        for field_name, err_detail in self.errors.items():
            user_msg = f'Error with url parameter "{field_name}": ' + str(err_detail[0])
            err_lines.append(user_msg)

        return ' '.join(err_lines)


class SignedUrlSerializer(serializers.Serializer):
    """
    Parameters required for each signed url
    @todo: add parser for incoming camel_case to snake_case transform
    """
    name = serializers.ChoiceField(choices=dv_static.REQUIRED_DV_URL_NAME_CHOICES)
    httpMethod = serializers.ChoiceField(choices=dv_static.HTTP_METHOD_CHOICES)
    signedUrl = serializers.URLField()
    timeOut = serializers.IntegerField()

    def validate_timeOut(self, value: int) -> int:
        """
        Check that 'time_out' is >= 1
        """
        if value < 1:
            raise serializers.ValidationError('This field must be 1 or greater.')
        return value

    def validate_signedUrl(self, value: str) -> str:
        """
        Check the url parameters exist and are valid
        @param value:
        @return:
        """
        url_dict = None
        try:
            url_dict = dict(parse.parse_qsl(parse.urlsplit(value).query))
        except AttributeError:
            raise serializers.ValidationError(f'This is not a valid url. ({value})')

        if not url_dict:
            raise serializers.ValidationError(f'No url parameters were found.')

        url_serializer = SingleSignedUrlSerializer(data=url_dict)
        if not url_serializer.is_valid():
            raise serializers.ValidationError(url_serializer.get_errors_in_oneline())

        return value

    def get_errors_in_oneline(self) -> str:
        """
        Combine errors into single line
        @return:
        """
        assert self.is_valid() is False, "Check that is_valid() is False before using this method."

        err_lines = []
        for field_name, err_detail in self.errors.items():
            user_msg = f'Error with url parameter "{field_name}": ' + str(err_detail[0])
            err_lines.append(user_msg)

        return ' '.join(err_lines)


class SignedUrlGroup(serializers.Serializer):
    signedUrls = serializers.JSONField()

    def validate_signedUrls(self, value: list) -> list:
        """
        Iterate through the API chunks
        """
        url_cnt = 0
        required_urls = dv_static.REQUIRED_DV_URL_NAMES[:]
        for url_info in value:
            serializer = SignedUrlSerializer(data=url_info)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.get_errors_in_oneline())
            url_cnt += 1
            if url_info.get('name') in required_urls:
                required_urls.remove(url_info.get('name'))

        if required_urls:
            user_msg = (f'{dv_static.ERR_MSG_EXPECTED_4_SIGNED_URLS}.'
                        ' Did not find url(s): %s.') % (', '.join(required_urls))
            raise serializers.ValidationError(user_msg)

        if url_cnt != 4:
            raise serializers.ValidationError(dv_static.ERR_MSG_EXPECTED_4_SIGNED_URLS)

        return list


"""
docker-compose run server python manage.py shell

from urllib import parse
from opendp_apps.dataverses.serializers import SingleSignedUrlSerializer

value = 'http://host.docker.internal:8089/api/users/:me?until=2022-08-08T11:18:28.368&user=dataverseAdmin&method=GET&token=bad3cbfff29bb2c3f8baa168dd20c86444c3a710195b9e25915eca4cc41791f84c5c3be08ec6a0a5f52573fa86876714d00e807c223572e143f92149525f29b2'

url_dict = dict(parse.parse_qsl(parse.urlsplit(value).query))

serializer = SingleSignedUrlSerializer(data=url_dict)
serializer.is_valid():
"""
