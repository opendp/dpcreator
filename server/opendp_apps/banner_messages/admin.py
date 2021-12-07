from django.contrib import admin

from .models import BannerMessage

class BannerMessageAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
    list_filter = ('active', 'is_timed_message', 'type')#, 'editor')
    list_editable = ['sort_order']
    list_display = ('name',
                    'active',
                    'type',
                    'sort_order',
                    'is_timed_message',
                    'editor',
                    'created',)
    readonly_fields = ('id', 'object_id', 'created', 'updated', 'editor',)
    fieldsets = (
        (None, {
            'fields': ('name', 'active', 'type', 'sort_order', 'content')
        }),
        ('Advanced - Timed messages. To use: Set "Active" to True and all 3 variables below:', {
            'fields': ('is_timed_message', 'view_start_time', 'view_stop_time'),
        }),
        ('Read-only fields.', {
            'fields': ('id', 'object_id', 'editor', 'created', 'updated'), #
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.editor = request.user
        super().save_model(request, obj, form, change)

admin.site.register(BannerMessage, BannerMessageAdmin)