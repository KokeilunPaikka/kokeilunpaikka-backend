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

    class Meta:
        model = Experiment
        fields = (
            'stage_id',
            'theme_ids',
        )
