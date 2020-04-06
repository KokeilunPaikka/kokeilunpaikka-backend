from rest_framework import serializers

from ..experiments.serializers import ExperimentListSerializer
from ..utils.serializers import ThumbnailImageField
from .models import LibraryItem


class LibraryItemBaseSerializer(serializers.ModelSerializer):
    image_url = ThumbnailImageField(
        size='list_image',
        source='image',
    )

    class Meta:
        model = LibraryItem
        fields = (
            'id',
            'description',
            'image_url',
            'lead_text',
            'name',
            'slug',
        )

    def to_representation(self, instance):
        # Make sure appropriate default values are returned for dot source
        # fields in the name of uniformity.
        data = super().to_representation(instance)
        if data['image_url'] is None:
            data['image_url'] = ''
        return data


class LibraryItemListSerializer(LibraryItemBaseSerializer):
    pass


class LibraryItemRetrieveSerializer(LibraryItemBaseSerializer):
    experiments = ExperimentListSerializer(
        many=True,
    )
    image_url = ThumbnailImageField(
        size='hero_image',
        source='image',
    )

    class Meta(LibraryItemBaseSerializer.Meta):
        fields = LibraryItemBaseSerializer.Meta.fields + (
            'experiments',
        )
