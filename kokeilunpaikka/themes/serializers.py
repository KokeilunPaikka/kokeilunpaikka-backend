from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Theme


class ThemeSerializer(serializers.ModelSerializer):
    # This translatable field had to be declared separately
    name = serializers.CharField()

    def create(self, validated_data):
        """Create a new instance and make sure the theme being created
        has capitalized first letter and that the name doesn't correlate
        with created themes.
        """
        validated_data['name'] = validated_data.get('name').capitalize()
        duplicates = Theme.objects.filter(translations__name__iexact=validated_data.get('name'))
        if duplicates.count() > 0:
            raise serializers.ValidationError(_(
                'No duplicate themes are allowed.'
            ))
        return super().create(validated_data)

    class Meta:
        model = Theme
        fields = (
            'id',
            'is_curated',
            'name',
        )
        read_only_fields = (
            'is_curated',
        )
