from django.contrib import admin

from .models import \
    (DataSetInfo, DataverseFileInfo, UploadFileInfo)

class DataSetInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
    list_filter = ('source', 'creator')
    list_display = ('name',
                    'creator',
                    'object_id',
                    'source',
                    'updated',
                    'created',)
    readonly_fields = ('id', 'object_id', 'source', 'created', 'updated',)

admin.site.register(DataSetInfo, DataSetInfoAdmin)


class DataverseFileInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
    list_filter = ('source', 'creator')
    list_display = ('id', 'name',
                    'object_id',
                    'dataset_doi',
                    'dataverse_file_id',
                    'creator',
                    'dv_installation',
                    'updated',
                    'created',)
    readonly_fields = ('id', 'object_id', 'source', 'created', 'updated',)
admin.site.register(DataverseFileInfo, DataverseFileInfoAdmin)

class UploadFileInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
    list_filter = ('source', 'creator')
    list_display = ('name',
                    'source_file',
                    'creator',
                    'updated',
                    'created',)
    readonly_fields = ('id', 'source', 'created', 'updated',)
admin.site.register(UploadFileInfo, UploadFileInfoAdmin)

