from django.contrib import admin
from opendp_apps.dataverses.models import \
    (DataverseHandoff,
     ManifestTestParams,
     RegisteredDataverse)


class DataverseHandoffAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'object_id', 'site_url')
    save_on_top = True
    list_filter = ('site_url', )
    readonly_fields = ('object_id',)


class RegisteredDataverseAdmin(admin.ModelAdmin):
    search_fields = ('name', 'dataverse_url', 'notes')
    list_display = ('name', 'dataverse_url', 'active', 'notes')
    save_on_top = True
    list_filter = ('active', )


class ManifestTestParamsAdmin(admin.ModelAdmin):
    search_fields = ('name', 'fileId', 'site_url')
    list_display = ('name', 'fileId', 'site_url',
                    'dataverse_incoming_link_2', 'use_mock_dv_api',
                    'filePid', 'datasetPid')
    save_on_top = True
    list_filter = ('site_url', )
    readonly_fields = ('dataverse_incoming_link_2',
                       'view_as_dict_link',
                       'mock_user_info_link',
                       'ddi_info_link',
                       'schema_org_info_link')


admin.site.register(DataverseHandoff, DataverseHandoffAdmin)
admin.site.register(RegisteredDataverse, RegisteredDataverseAdmin)
admin.site.register(ManifestTestParams, ManifestTestParamsAdmin)
