from django_filters import rest_framework as filters

from ..themes.models import Theme
from .models import Experiment, ExperimentChallenge


class ExperimentChallengeFilter(filters.FilterSet):
    theme_ids = filters.ModelChoiceFilter(
        queryset=Theme.objects.all(),
        field_name='themes'
    )

    class Meta:
        model = ExperimentChallenge
        fields = (
            'theme_ids',
        )


class ExperimentFilter(filters.FilterSet):
    theme_ids = filters.ModelChoiceFilter(
        queryset=Theme.objects.all(),
        field_name='themes'
    )
    first_load = filters.BooleanFilter(method="first_load_filter")

    class Meta:
        model = Experiment
        fields = (
            'stage_id',
            'theme_ids',
        )

    def first_load_filter(self, queryset, name, value):
        if value is True:
            user_profile = getattr(self.request.user, 'profile', False)
            if user_profile and user_profile.interested_in_themes.count():
                return queryset.filter(themes__in=user_profile.interested_in_themes.all())

        return queryset
