from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from opendp_apps.opendp_auth.models import User

class OpenDPUserAdmin(UserAdmin):
    pass
    # customize later
    #list_filter = ('company__name',)
admin.site.register(User, OpenDPUserAdmin)
