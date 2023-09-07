from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from opendp_apps.release_schemas.models import ReleaseInfoSchema
from opendp_apps.release_schemas.validators import \
    (format_semantic_version)


class ReleaseInfoSchemaForm(ModelForm):
    class Meta:
        model = ReleaseInfoSchema
        fields = '__all__'

    def clean(self):
        """Validate the data. Check that the version number is in the name"""
        version = self.cleaned_data.get("version")
        schema = self.cleaned_data.get("schema")

        errors = {}
        if version and schema:
            schema_version = schema.get('version', None)
            if schema_version is None:
                errors['schema'] = _(f'The schema requires a "version" key.')
            elif not version == schema_version:
                errors['version'] = _((f'The version, "{version}", does not match the'
                                       f' schema\'s "version", which has the value'
                                       f' "{schema_version}".'))

        if errors:
            raise ValidationError(errors)

        return self.cleaned_data

    def clean_version(self):
        """Format the version number"""
        data = self.cleaned_data.get('version')
        if not data:
            raise ValidationError('"version" is required')

        data = format_semantic_version(data)

        return data
