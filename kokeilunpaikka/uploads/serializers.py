from rest_framework import serializers

from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(
        source='image',
    )

    class Meta:
        model = Image
        fields = (
            'id',
            'url',
        )
