from django.contrib import admin
from .models import \
    (DepositorSetupInfo, AnalysisPlan, ReleaseInfo)


class DepositorSetupInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('dataset__name',)
    list_filter = ('is_complete', )
    list_display = ('dataversefileinfo',
                    'user_step',
                    'epsilon',
                    'updated',
                    'created',)
    readonly_fields = ('id', 'is_complete', 'created', 'updated',)


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
    readonly_fields = ('id', 'is_complete', 'created', 'updated',)


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


admin.site.register(DepositorSetupInfo, DepositorSetupInfoAdmin)
admin.site.register(AnalysisPlan, AnalysisPlanAdmin)
admin.site.register(ReleaseInfo, ReleaseInfoAdmin)

