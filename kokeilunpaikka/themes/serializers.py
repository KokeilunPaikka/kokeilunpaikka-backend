from rest_framework import serializers

from .models import Theme


class ThemeSerializer(serializers.ModelSerializer):
    # This translatable field had to be declared separately
    name = serializers.CharField()

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
