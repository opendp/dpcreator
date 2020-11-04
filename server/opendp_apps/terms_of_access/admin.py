from django.contrib import admin
from .models import TermsOfAccess, TermsOfAccessLog


class TermsOfAccessAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name', 'description')
    list_filter = ('active',)
    list_display = ('name',
                    'version',
                    'active',
                    'description',
                    'updated',
                    'created',)
    readonly_fields = ('created', 'updated',)


class TermsOfAccessLogAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('terms_of_access__name',
                     'dataset_info__name')
    list_filter = ('user', 'dataset_info')
    list_display = ('user',
                    'dataset_info',
                    'terms_of_access',
                    'updated',
                    'created',)
    readonly_fields = ('created', 'updated',)


admin.site.register(TermsOfAccess, TermsOfAccessAdmin)
admin.site.register(TermsOfAccessLog, TermsOfAccessLogAdmin)
