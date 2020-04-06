from django.contrib import admin

from parler.admin import TranslatableAdmin

from .models import Theme


@admin.register(Theme)
class ThemeAdmin(TranslatableAdmin):
    fields = (
        'name',
        'is_curated',
        'created_by',
        'created_at',
        'updated_at',
    )
    list_display = (
        'id',
        'name',
        'is_curated',
    )
    list_display_links = (
        'id',
        'name',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    def get_changeform_initial_data(self, request):
        """Set themes created using Django admin to curated by default."""
        return {'is_curated': 'True'}
