from django.contrib import admin

# Register your models here.
from django.contrib import admin

from opendp_apps.release_schemas.models import ReleaseInfoSchema
from opendp_apps.release_schemas.forms import ReleaseInfoSchemaForm

class ReleaseInfoSchemaAdmin(admin.ModelAdmin):
    form = ReleaseInfoSchemaForm
    save_on_top = True
    search_fields = ('name',)
    list_filter = ('is_published',)
    list_display = ('name',
                    'version',
                    'is_published',
                    'description',
                    'updated',
                    'created',)
    readonly_fields = ('object_id',
                       'sortable_version',
                       'schema_link',
                       'id_link',
                       'schema_display',
                       'created',
                       'updated',)
admin.site.register(ReleaseInfoSchema, ReleaseInfoSchemaAdmin)
