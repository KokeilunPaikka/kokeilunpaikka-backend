from django.contrib import admin

from parler.admin import TranslatableAdmin

from .models import EditableText, SiteConfiguration


@admin.register(EditableText)
class EditableTextAdmin(TranslatableAdmin):
    fields = (
        'text_type',
        'text_value'
    )
    list_display = (
        'text_type',
        'text_value'
    )


@admin.register(SiteConfiguration)
class SiteConfigurationTextAdmin(admin.ModelAdmin):
    filter_horizontal = (
        'featured_experiments',
    )
    fields = (
        'active',
        'front_page_image',
        'front_page_image_opacity',
        'top_menu_opacity',
        'featured_experiments',
        'funded_experiments_amount'
    )
    list_display = (
        'configuration_title',
        'active'
    )

    def configuration_title(self, obj):
        return f'Site Configuration #{obj.id}'
