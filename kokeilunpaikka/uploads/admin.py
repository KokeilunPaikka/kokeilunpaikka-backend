from django.contrib import admin

from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    fields = (
        'image',
        'uploaded_by',
        'created_at',
        'updated_at',
    )
    list_display = (
        'id',
        'image',
        'uploaded_by',
        'created_at',
    )
    list_display_links = (
        'id',
        'image',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
