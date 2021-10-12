from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from .models import UserLookingForOption
from ..themes.models import Theme


class UserFilter(filters.FilterSet):
    theme_id = filters.ModelChoiceFilter(
        queryset=Theme.objects.all(),
        field_name='profile__interested_in_themes'
    )
    looking_for = filters.ModelChoiceFilter(
        queryset=UserLookingForOption.objects.all(),
        field_name='profile__looking_for'
    )
    offering = filters.ModelChoiceFilter(
        queryset=UserLookingForOption.objects.all(),
        field_name='profile__offering'
    )

    class Meta:
        model = get_user_model()
        fields = (
            'profile__interested_in_themes',
            'profile__offering',
            'profile__looking_for',
        )
