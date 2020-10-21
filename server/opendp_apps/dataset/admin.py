from django.contrib import admin

from .models import DataSetInfo, DataverseFileInfo

class DataSetInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
    list_filter = ('source', 'creator')
    list_display = ('name',
                    'creator',
                    'source',
                    'updated',
                    'created',)
    readonly_fields = ('created', 'updated',)

admin.site.register(DataSetInfo, DataSetInfoAdmin)


class DataverseFileInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
    list_filter = ('source', 'creator')
    list_display = ('name',
                    'doi',
                    'dataverse_file_id',
                    'creator',
                    'installation_name',
                    'updated',
                    'created',)
    readonly_fields = ('source', 'created', 'updated',)

admin.site.register(DataverseFileInfo, DataverseFileInfoAdmin)

