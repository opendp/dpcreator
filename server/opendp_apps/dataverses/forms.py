from django.forms import ModelForm

from opendp_apps.dataverses.models import DataverseHandoff


class DataverseHandoffForm(ModelForm):
    class Meta:
        model = DataverseHandoff
        exclude = ['name', 'object_id', 'created', 'modified']
