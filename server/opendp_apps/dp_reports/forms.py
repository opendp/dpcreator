import json
from collections import OrderedDict

from django import forms
from django.core.exceptions import ValidationError


class ReportForm(forms.Form):
    """Create a PDF from a JSON Release"""
    json_release = forms.CharField(widget=forms.Textarea)

    def clean_json_release(self):
        """Format into a JSON dict"""
        release_content = self.cleaned_data['json_release']
        try:
            release_dict = json.loads(release_content, object_pairs_hook=OrderedDict)
        except json.JSONDecodeError as err_obj:
            user_msg = f'Not a valid JSON doc. {err_obj}'
            raise ValidationError(user_msg)

        return release_dict
