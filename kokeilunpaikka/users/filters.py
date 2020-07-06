from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from ..themes.models import Theme


class UserFilter(filters.FilterSet):
    theme_id = filters.ModelChoiceFilter(
        queryset=Theme.objects.all(),
        field_name='profile__interested_in_themes'
    )

    class Meta:
        model = get_user_model()
        fields = (
            'profile__interested_in_themes',
        )
