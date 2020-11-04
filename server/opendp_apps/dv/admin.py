from django.contrib import admin
from opendp_apps.dv.models import RegisteredDataverse


class RegisteredDataverseAdmin(admin.ModelAdmin):
    search_fields = ('name', 'dataverse_url', 'notes')
    list_display = ('name', 'dataverse_url', 'active', 'notes')
    save_on_top = True
    list_filter  = ('active', )







admin.site.register(RegisteredDataverse, RegisteredDataverseAdmin)
