from django.contrib import admin

from .models import \
    (AnalysisPlan,
     ReleaseEmailRecord,
     ReleaseInfo,
     AuxiliaryFileDepositRecord)


class AnalysisPlanAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('dataset__name',)
    list_filter = ('is_complete', 'user_step', 'analyst', 'dataset')
    list_display = ('name',
                    'dataset',
                    'analyst',
                    'is_complete',
                    'user_step',
                    'updated',
                    'created',)
    readonly_fields = ('id',
                       'object_id',
                       'dataset',
                       'analyst',
                       'release_info',
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
                       'dp_release_json', 'epsilon_used',
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


class ReleaseEmailRecordAdmin(admin.ModelAdmin):
    save_on_top = True
    list_filter = ('success',)
    list_display = ('release_info',
                    'success',
                    'to_email',
                    'from_email',
                    'updated',
                    'created',)
    readonly_fields = ('release_info',
                       'success',
                       'note',
                       'pdf_attached',
                       'json_attached',
                       'subject',
                       'to_email',
                       'from_email',
                       'email_content',
                       'id',
                       'object_id',
                       'created', 'updated',)


admin.site.register(AnalysisPlan, AnalysisPlanAdmin)
admin.site.register(ReleaseInfo, ReleaseInfoAdmin)
admin.site.register(AuxiliaryFileDepositRecord, AuxiliaryFileDepositRecordAdmin)
admin.site.register(ReleaseEmailRecord, ReleaseEmailRecordAdmin)
