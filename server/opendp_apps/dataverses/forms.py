from django.forms import ModelForm, ValidationError

from opendp_apps.dataverses.models import DataverseHandoff, DataverseParams, RegisteredDataverse

class DataverseParamsForm(ModelForm):

    class Meta:
        model = DataverseParams
        exclude = ['object_id', 'created', 'modified']

    def clean_siteUrl(self):

        dataverse_url = self.cleaned_data.get('siteUrl')

        try:
            registerd_dataverse = RegisteredDataverse.objects.get(dataverse_url=dataverse_url)
        except RegisteredDataverse.DoesNotExist:
            user_msg = (f'The Dataverse siteUrl was not recognized: {dataverse_url}')
            raise ValidationError(user_msg)

        return registerd_dataverse


class DataverseParamsSiteUrlForm(ModelForm):

    class Meta:
        model = DataverseParams
        fields = ['siteUrl']

    def clean_siteUrl(self):

        dataverse_url = self.cleaned_data.get('siteUrl')

        try:
            registerd_dataverse = RegisteredDataverse.objects.get(dataverse_url=dataverse_url)
        except RegisteredDataverse.DoesNotExist:
            user_msg = (f'The Dataverse siteUrl was not recognized: {dataverse_url}')
            raise ValidationError(user_msg)

        return registerd_dataverse


class DataverseHandoffForm(ModelForm):
    class Meta:
        model = DataverseHandoff
        exclude = ['name', 'object_id', 'created', 'modified']
