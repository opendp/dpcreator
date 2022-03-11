from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from opendp_apps.user.models import OpenDPUser, DataverseUser


class OpenDPUserAdmin(UserAdmin):
    save_on_top = True
    list_display_links = ('email', 'username',)
    list_display = ('username', 'email', 'pk', 'handoff_id', 'first_name', 'last_name', 'object_id')


# pass
# customize later
# list_filter = ('company__name',)


class DataverseUserAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name', 'description')
    list_filter = ('dv_installation',)
    list_display = ('user',
                    'dv_installation',
                    #'persistent_id',
                    'object_id',
                    'email',
                    'updated',
                    'created',)
    readonly_fields = ('created', 'updated', 'object_id')


admin.site.register(OpenDPUser, OpenDPUserAdmin)
admin.site.register(DataverseUser, DataverseUserAdmin)
