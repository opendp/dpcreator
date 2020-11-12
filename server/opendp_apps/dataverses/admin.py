from django.contrib import admin
from opendp_apps.dataverses.models import ManifestTestParams, RegisteredDataverse


class RegisteredDataverseAdmin(admin.ModelAdmin):
    search_fields = ('name', 'dataverse_url', 'notes')
    list_display = ('name', 'dataverse_url', 'active', 'notes')
    save_on_top = True
    list_filter  = ('active', )



class ManifestTestParamsAdmin(admin.ModelAdmin):
    search_fields = ('name', 'fileId', 'siteUrl')
    list_display = ('name', 'fileId', 'siteUrl', 'dataverse_incoming_link', 'filePid', 'datasetPid')
    save_on_top = True
    list_filter  = ('siteUrl', )
    readonly_fields = ('dataverse_incoming_link','user_info_link',)



admin.site.register(RegisteredDataverse, RegisteredDataverseAdmin)
admin.site.register(ManifestTestParams, ManifestTestParamsAdmin)
