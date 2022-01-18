from django.contrib import admin
from .models import \
    (DepositorSetupInfo, AnalysisPlan, ReleaseInfo, AuxiliaryFileDepositRecord)


class DepositorSetupInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('dataset__name',)
    list_filter = ('is_complete', )
    list_display = ('dataversefileinfo',
                    'user_step',
                    'epsilon',
                    'updated',
                    'created',)
    readonly_fields = ('id',
                       'object_id',
                       'is_complete',
                       'variable_info_display',
                       'created',
                       'updated',)


class AnalysisPlanAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('dataset__name',)
    list_filter = ('is_complete', 'user_step', 'analyst', 'dataset')
    list_display = ('name',
                    'dataset',
                    'analyst',
                    'is_complete',
                    'user_step',
                    #'epsilon',
                    'updated',
                    'created',)
    readonly_fields = ('id',
                       'object_id',
                       'is_complete',
                       'variable_info_display',
                       'created',
                       'updated',)


class AuxiliaryFileDepositRecordInline(admin.TabularInline):
    model = AuxiliaryFileDepositRecord
    extra = 0


class ReleaseInfoAdmin(admin.ModelAdmin):
    inlines = (AuxiliaryFileDepositRecordInline,)
    save_on_top = True
    search_fields = ('dataset__name',)
    list_filter = ('dataset__source', 'dataset',)
    list_display = ('dataset',
                    'epsilon_used',
                    'updated',
                    'created',)
    readonly_fields = ('id',
                       'object_id',
                       'dataset',
                       'dp_release', 'epsilon_used',
                       'dataverse_deposit_info_json',
                       'download_json_url',
                       'download_pdf_url',
                       'created', 'updated',)


class AuxiliaryFileDepositRecordAdmin(admin.ModelAdmin):
    save_on_top = True
    list_filter = ('deposit_success', 'dv_auxiliary_type', 'dv_auxiliary_version',)
    list_display = ('name',
                    'deposit_success',
                    'dv_auxiliary_type',
                    'dv_auxiliary_version',
                    'updated',
                    'created',)
    readonly_fields = ('id',
                       'object_id',
                       'release_info',
                       'json_string_html',
                       'created', 'updated',)


admin.site.register(DepositorSetupInfo, DepositorSetupInfoAdmin)
admin.site.register(AnalysisPlan, AnalysisPlanAdmin)
admin.site.register(ReleaseInfo, ReleaseInfoAdmin)
admin.site.register(AuxiliaryFileDepositRecord, AuxiliaryFileDepositRecordAdmin)

