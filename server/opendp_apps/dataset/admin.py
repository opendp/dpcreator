from django.conf import settings
from django.contrib import admin
from django.core.management import get_commands, call_command
from django.http import HttpResponseRedirect
from django.urls import path

from .models import \
    (DataSetInfo, DataverseFileInfo, UploadFileInfo)


class DataSetInfoAdmin(admin.ModelAdmin):
    change_list_template = "admin/dataset/datasetinfo_change_list.html"

    save_on_top = True
    search_fields = ('name',)
    list_filter = ('source', 'creator')
    list_display = ('name',
                    'creator',
                    'object_id',
                    'source',
                    'updated',
                    'created',)
    readonly_fields = ('id', 'object_id', 'source', 'created', 'updated',)

    def changelist_view(self, request, extra_context=None):
        extra_context = {'allow_demo_loading': settings.ALLOW_DEMO_LOADING}
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()

        if 'setup_demo' in get_commands():
            setup_demo_urls = [path('setup-demo/', self.setup_demo_from_admin),
                               path('clear-test-data/', self.clear_test_data_from_admin)]
            return setup_demo_urls + urls
        return urls

    def setup_demo_from_admin(self, request):
        """Run setup demo command. Only available to superusers"""
        if not request.user.is_superuser:
            user_msg = "The setup_demo command is not available! (Not a superuser)"
            self.message_user(request, user_msg)
        elif 'setup_demo' not in get_commands():
            user_msg = "The setup_demo command is not available! (Cypress settings not in place)"
            self.message_user(request, user_msg)
        else:
            call_command('setup_demo')
            user_msg = "Loaded demo data. (Other data has been deleted)"
            self.message_user(request, user_msg)
        return HttpResponseRedirect("../")

    def clear_test_data_from_admin(self, request):
        """Run clear_test_data. Only available to superusers"""
        if not request.user.is_superuser:
            user_msg = "The setup_demo command is not available! (Not a superuser)"
            self.message_user(request, user_msg)
        elif 'clear_test_data' not in get_commands():
            user_msg = "The clear_test_data command is not available! (Cypress settings not in place)"
            self.message_user(request, user_msg)
        else:
            call_command('clear_test_data')
            user_msg = "Test data cleared."
            self.message_user(request, user_msg)
        return HttpResponseRedirect("../")


admin.site.register(DataSetInfo, DataSetInfoAdmin)


class DataverseFileInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
    list_filter = ('source', 'creator')
    list_display = ('id', 'name',
                    'object_id',
                    'dataset_doi',
                    'dataverse_file_id',
                    'creator',
                    'dv_installation',
                    'updated',
                    'created',)
    list_display_links = ('id', 'name')
    readonly_fields = ('id', 'object_id', 'source', 'created', 'updated',)


admin.site.register(DataverseFileInfo, DataverseFileInfoAdmin)


class UploadFileInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
    list_filter = ('source', 'creator')
    list_display = ('name',
                    # 'data_file',
                    'creator',
                    'updated',
                    'created',)
    readonly_fields = ('id', 'source', 'created', 'updated',)


admin.site.register(UploadFileInfo, UploadFileInfoAdmin)
