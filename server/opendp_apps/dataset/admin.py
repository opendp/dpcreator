from django.contrib import admin

from .models import \
    (DataSetInfo, DataverseFileInfo,
     DepositorSetupInfo, ReleaseInfo)

class DataSetInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
    list_filter = ('source', 'creator')
    list_display = ('name',
                    'creator',
                    'source',
                    'updated',
                    'created',)
    readonly_fields = ('id', 'source', 'created', 'updated',)

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
    readonly_fields = ('id', 'source', 'created', 'updated',)
admin.site.register(DataverseFileInfo, DataverseFileInfoAdmin)



class DepositorSetupInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('dataset__name',)
    list_filter = ('is_complete', 'dataset__source')
    list_display = ('dataset',
                    'user_step',
                    'epsilon',
                    'updated',
                    'created',)
    readonly_fields = ('id', 'is_complete', 'created', 'updated',)

admin.site.register(DepositorSetupInfo, DepositorSetupInfoAdmin)



class ReleaseInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('dataset__name',)
    list_filter = ('dataset__source', 'dataset',)
    list_display = ('analysis_plan',
                    'dataset',
                    'epsilon_used',
                    'updated',
                    'created',)
    readonly_fields = ('id',
                       'dataset', 'analysis_plan',
                       'dp_release', 'epsilon_used',
                       'created', 'updated',)

admin.site.register(ReleaseInfo, ReleaseInfoAdmin)

