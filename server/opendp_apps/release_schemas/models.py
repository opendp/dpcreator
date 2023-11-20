import json
import logging

from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from rest_framework import reverse as drf_reverse

from opendp_apps.model_helpers.models import TimestampedModelWithUUID
from opendp_apps.release_schemas import static_vals as rstatic
from opendp_apps.release_schemas.validators import \
    (validate_semantic_version_number,
     validate_json_schema,
     get_sortable_semantic_version)

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class ReleaseInfoSchema(TimestampedModelWithUUID):
    """
    Schema Information for a release
    """
    version = models.CharField(max_length=50,
                               unique=True,
                               verbose_name='Version number',
                               help_text='Semantic version. Example: 1.4.2',
                               validators=[validate_semantic_version_number])

    title = models.CharField(max_length=128,
                             blank=True,
                             help_text='(auto-generated) Value of the schema\'s "title" property.')

    description = models.TextField(blank=True, help_text='Description of the schema')

    is_published = models.BooleanField(default=False)

    schema = models.JSONField(help_text='JSON schema',
                              validators=[validate_json_schema])

    schema_link = models.URLField(blank=True,
                                  help_text=('(auto-filled) Value of the schema\'s'
                                             ' "$schema" property, if available'))

    id_link = models.URLField(blank=True,
                              help_text=('(auto-filled) Value of the schema\'s "$id"'
                                         ' property, if available'))

    sortable_version = models.CharField(max_length=50,
                                        help_text=('(auto-filled) Sortable version number'
                                                   ' of the schema.'))

    class Meta:
        ordering = ['-sortable_version']

    def __str__(self):
        return f'{self.title} ({self.version})'

    def save(self):
        """Create a sortable version of the semantic version number"""
        # self.version = format_semantic_version(self.version)
        self.sortable_version = get_sortable_semantic_version(self.version)
        self.schema_link = self.get_schema_value('$schema', rstatic.SCHEMA_FIELD_NOT_SET)
        self.title = self.get_schema_value('title', f'Version {self.version}')
        self.id_link = self.get_schema_value('$id', rstatic.SCHEMA_FIELD_NOT_SET)

        super().save()

    def get_api_schema_url(self):
        """Return the url for this schema, based on the version number. e.g. '/api/schema/0.2.0/' """
        return drf_reverse('schema-detail', kwargs=dict(version=self.version))

    @staticmethod
    def get_latest_schema():
        """Return the latest schema"""
        return ReleaseInfoSchema.objects.filter(is_published=True).first()

    @mark_safe
    def schema_display(self):
        """Return a string representation of the schema for the admin"""
        if self.schema:
            return """<pre>{}</pre>""".format(json.dumps(self.schema, indent=4))

        return '(not available)'

    @mark_safe
    def get_schema_value(self, key, default=None):
        """Return the link to the schema, using the keyword '$schema' """
        if not self.schema:
            return None

        return self.schema.get(key, default)

    def get_title(self):
        if not self.schema:
            return f'Version {self.version}'
        return self.schema.get('title', f'Version {self.version}')

    '''
    def get_schema_url_for_release(self):
        """Return the schema url for the release"""
        release_schema = self.id_link
        if not self.schema:
            return None

        return self.schema.get('$id', None)
    '''
