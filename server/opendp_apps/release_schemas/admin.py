# Register your models here.
from django.contrib import admin

from opendp_apps.release_schemas.forms import ReleaseInfoSchemaForm
from opendp_apps.release_schemas.models import ReleaseInfoSchema


class ReleaseInfoSchemaAdmin(admin.ModelAdmin):
    form = ReleaseInfoSchemaForm
    save_on_top = True
    search_fields = ('title',)
    list_filter = ('is_published',)
    list_display = ('version',
                    'title',
                    'is_published',
                    'description',
                    'updated',
                    'created',)
    readonly_fields = ('title',
                       'sortable_version',
                       'schema_link',
                       'id_link',
                       'schema_display',
                       'created',
                       'updated',)
    fields = ['version',
              'title',
              'is_published',
              'schema',
              'description',
              'schema_link',
              'id_link',
              'schema_display',
              'created',
              'updated', ]


admin.site.register(ReleaseInfoSchema, ReleaseInfoSchemaAdmin)
