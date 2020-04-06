from django.contrib import admin

from parler.admin import TranslatableAdmin

from .models import UserLookingForOption, UserProfile, UserStatusOption


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    fields = (
        'user',
        'description',
        'image',
        'interested_in_themes',
        'looking_for',
        'status',
        'facebook_url',
        'instagram_url',
        'linkedin_url',
        'twitter_url',
        'expose_email_address',
        'created_at',
        'updated_at',
    )
    filter_horizontal = (
        'interested_in_themes',
        'looking_for',
    )
    list_display = (
        'id',
        'user',
    )
    list_display_links = (
        'id',
        'user',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(UserLookingForOption)
class UserLookingForOptionAdmin(TranslatableAdmin):
    fields = (
        'value',
        'created_at',
        'updated_at',
    )
    list_display = (
        'id',
        'value',
    )
    list_display_links = (
        'id',
        'value',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(UserStatusOption)
class UserStatusOptionAdmin(TranslatableAdmin):
    fields = (
        'value',
        'created_at',
        'updated_at',
    )
    list_display = (
        'id',
        'value',
    )
    list_display_links = (
        'id',
        'value',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
