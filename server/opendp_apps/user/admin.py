from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from opendp_apps.user.models import OpenDPUser

class OpenDPUserAdmin(UserAdmin):
    pass
    # customize later
    #list_filter = ('company__name',)
admin.site.register(OpenDPUser, OpenDPUserAdmin)
