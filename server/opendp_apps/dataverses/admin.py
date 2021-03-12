from django.contrib import admin
from opendp_apps.dataverses.models import \
    (DataverseHandoff,
     ManifestTestParams,
     RegisteredDataverse)


class DataverseHandoffAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'object_id', 'siteUrl')
    save_on_top = True
    list_filter = ('siteUrl', )


class RegisteredDataverseAdmin(admin.ModelAdmin):
    search_fields = ('name', 'dataverse_url', 'notes')
    list_display = ('name', 'dataverse_url', 'active', 'notes')
    save_on_top = True
    list_filter = ('active', )


class ManifestTestParamsAdmin(admin.ModelAdmin):
    search_fields = ('name', 'fileId', 'siteUrl')
    list_display = ('name', 'fileId', 'siteUrl',
                    'dataverse_incoming_link_2', 'use_mock_dv_api',
                    'filePid', 'datasetPid')
    save_on_top = True
    list_filter = ('siteUrl', )
    readonly_fields = ('dataverse_incoming_link_2',
                       'view_as_dict_link',
                       'mock_user_info_link',
                       'ddi_info_link',
                       'schema_org_info_link')


# Commenting out, not sure why this was here....
# DataverseHandoffAdmin
admin.site.register(DataverseHandoff, DataverseHandoffAdmin)
admin.site.register(RegisteredDataverse, RegisteredDataverseAdmin)
admin.site.register(ManifestTestParams, ManifestTestParamsAdmin)
