from django.contrib import admin

from parler.admin import TranslatableAdmin

from .models import LibraryItem


@admin.register(LibraryItem)
class LibraryItemAdmin(TranslatableAdmin):
    fields = (
        'name',
        'slug',
        'lead_text',
        'description',
        'image',
        'themes',
        'is_visible',
        'created_at',
        'updated_at',
    )
    filter_horizontal = (
        'themes',
    )
    list_display = (
        'id',
        'name',
        'is_visible',
    )
    list_display_links = (
        'id',
        'name',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    def get_prepopulated_fields(self, request, obj=None):
        # Can't use `prepopulated_fields` because it breaks the admin
        # validation for translated fields.
        #
        # This is the official django-parler workaround.
        return {
            'slug': ('name',)
        }
