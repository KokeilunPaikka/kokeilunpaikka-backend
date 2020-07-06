from rest_framework import serializers

from .models import EditableText, SiteConfiguration
from ..experiments.serializers import ExperimentListSerializer


class EditableTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditableText
        fields = (
            'id',
            'text_type',
            'text_value'
        )


class SiteConfigurationSerializer(serializers.ModelSerializer):
    featured_experiments = ExperimentListSerializer(many=True)

    class Meta:
        model = SiteConfiguration
        fields = (
            'id',
            'front_page_image',
            'front_page_image_opacity',
            'top_menu_opacity',
            'featured_experiments',
            'funded_experiments_amount'
        )
