from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from kokeilunpaikka.users.models import UserProfile

from .models import User


class UserProfileInlineAdmin(admin.StackedInline):
    model = UserProfile
    extra = 1
    max_num = 1
    fields = (
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
    )
    filter_horizontal = (
        'interested_in_themes',
        'looking_for',
    )


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    change_list_template = 'admin/auth/user/change_list.html'
    inlines = (
        UserProfileInlineAdmin,
    )
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')
    ordering = ('-id',)


# Native Group admin is unnecessary as of now
admin.site.unregister(Group)
