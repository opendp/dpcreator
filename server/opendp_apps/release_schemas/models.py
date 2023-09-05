import json
import logging

from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe

from opendp_apps.model_helpers.models import TimestampedModelWithUUID
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

    name = models.CharField(max_length=128,
                            unique=True,
                            help_text='Name of the schema. Include the "Version number" in the name.')

    is_published = models.BooleanField(default=False)

    schema = models.JSONField(help_text='JSON schema',
                              validators=[validate_json_schema])

    schema_link = models.URLField(blank=True,
                                  help_text='(auto-filled) Link to the schema, using the keyword "$schema"')

    id_link = models.URLField(blank=True,
                              help_text='(auto-filled) Link to the "id", trying the keywords "id" and "$id"')

    description = models.TextField(blank=True)

    sortable_version = models.CharField(max_length=50,
                                        help_text='Auto-populated. Sortable version of the schema.')

    class Meta:
        ordering = ['-sortable_version']

    def __str__(self):
        return f'{self.name} ({self.version})'



    def save(self):
        """Create a sortable version of the semantic version number"""
        #self.version = format_semantic_version(self.version)
        self.sortable_version = get_sortable_semantic_version(self.version)
        self.schema_link = self.get_schema_link()
        self.id_link = self.get_id_link()

        super().save()

    @mark_safe
    def schema_display(self):
        """Return a string representation of the schema for the admin"""
        if self.schema:
            return """<pre>{}</pre>""".format(json.dumps(self.schema, indent=4))

        return '(not available)'

    @mark_safe
    def get_schema_link(self):
        """Return the link to the schema, using the keyword '$schema' """
        if not self.schema:
            return None

        return self.schema.get('$schema', None)

    @mark_safe
    def get_id_link(self):
        """Return the link to the 'id', trying the keywords 'id' and '$id' """
        if not self.schema:
            return None

        # try both "id" and "$id"
        id_link = self.schema.get('id', None)
        if not id_link:
            id_link = self.schema.get('$id', None)

        return id_link
