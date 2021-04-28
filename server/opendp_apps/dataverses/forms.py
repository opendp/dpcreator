from http import HTTPStatus

from django.contrib.auth import get_user_model
from django import forms

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import DataverseHandoff, RegisteredDataverse, DataverseParams


class DataverseUserHandlerForm(forms.Form):
    """Validate inputs of OpenDPUser.object_id and DataverseHandoff.object_id"""
    user_id = forms.CharField(label='OpenDPUser.object_id', max_length=36)
    dataverse_handoff_id = forms.CharField(label='DataverseHandoff.object_id', max_length=36)

    status_code = None

    def clean_dataverse_handoff_id(self):
        """Check that the DataverseHandoff object exists and check the site_url for validity.
        If everything looks good, return the object.DataverseHandoffForm"""
        dataverse_handoff_id = self.cleaned_data.get(dv_static.KEY_DV_HANDOFF_ID)

        try:
            dv_handoff = DataverseHandoff.objects.get(object_id=dataverse_handoff_id)
        except DataverseHandoff.DoesNotExist as ex_obj:
            self.status_code = HTTPStatus.NOT_FOUND
            user_msg = (f'The DataverseHandoff object was not found. ({dataverse_handoff_id})')
            raise forms.ValidationError(user_msg)

        if not dv_handoff.is_site_url_registered():
            user_msg = f'The Dataverse site_url ({dv_handoff.site_url}) is not registered'
            raise forms.ValidationError(user_msg)

        return dv_handoff

    def clean_user_id(self):
        """Check that the OpenDP user exists. If so, return it"""
        user_id = self.cleaned_data.get(dv_static.KEY_DP_USER_ID)

        user_model = get_user_model()
        try:
            opendp_user = user_model.objects.get(object_id=user_id)
        except user_model.DoesNotExist as ex_obj:
            self.status_code = HTTPStatus.NOT_FOUND
            user_msg = (f'The OpenDPUser object was not found. ({user_id})')
            raise forms.ValidationError(user_msg)

        return opendp_user

    def get_dv_handoff_and_opendp_user(self):
        """Return the DataverseHandoff and OpenDPUser objects. e.g (DataverseHandoff, OpenDPUser)"""
        assert self.is_valid(), "Check that '.is_valid()' is True before using this method"

        return (self.cleaned_data[dv_static.KEY_DV_HANDOFF_ID], \
                self.cleaned_data[dv_static.KEY_DP_USER_ID])

    def get_http_error_code(self):
        assert not self.is_valid(), "Check that '.is_valid()' is False before using this method"
        if self.status_code:
            return self.status_code
        return HTTPStatus.BAD_REQUEST

    def format_errors(self):
        """Combine error messages into single message user
        {"sender": [{"message": "Enter a valid email address.", "code": "invalid"}],
"subject": [{"message": "This field is required.", "code": "required"}]}
        """
        assert not self.is_valid(), "Check that '.is_valid()' is False before using this method"

        # -----------------------------------------------------
        # Iterate through error messages and concatenate them
        # -----------------------------------------------------
        outlines = []
        for field_name, msg_list in self.errors.get_json_data().items():
            for info in msg_list:
                if info['code'] in ['required', 'invalid']:
                    outlines.append(f"{field_name}: {info['message']}")
                else:
                    outlines.append(info['message'])
        num_msgs = len(outlines)
        if  num_msgs == 1:
            outlines.insert(0, 'Error found.')
        elif  num_msgs > 1:
            outlines.insert(0, f'{num_msgs} errors found.')

        return ' '.join(outlines)


class DataverseParamsSiteUrlForm(forms.ModelForm):

    class Meta:
        model = DataverseParams
        fields = ['site_url']

    def clean_site_url(self):

        dataverse_url = self.cleaned_data.get('site_url')

        try:
            registerd_dataverse = RegisteredDataverse.objects.get(dataverse_url=dataverse_url)
        except RegisteredDataverse.DoesNotExist:
            user_msg = (f'The Dataverse siteUrl was not recognized: {dataverse_url}')
            raise forms.ValidationError(user_msg)

        return registerd_dataverse
