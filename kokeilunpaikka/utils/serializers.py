from easy_thumbnails.templatetags.thumbnail import thumbnail_url
from rest_framework import serializers


class ThumbnailImageField(serializers.ImageField):
    """Image field that represents the image as an absolute URL to
    the thumbnail file.

    Alias of the size of the thumbnail must be given as parameter. Possible
    thumbnail aliases are set in the `THUMBNAIL_ALIASES` setting.
    """

    def __init__(self, *args, **kwargs):
        """Set thumbnail size required in representation."""
        self._thumbnail_size = kwargs.pop('size', None)

        if not self._thumbnail_size:
            raise RuntimeError('You must define size parameter.')

        super().__init__(*args, **kwargs)

    def to_representation(self, instance, request=None):
        request = request or self.context.get('request', None)

        if not request:
            raise RuntimeError(
                'Request object must be passed to the field within context '
                'data.'
            )

        if not instance:
            return None

        thumbnail_path = thumbnail_url(instance, self._thumbnail_size)
        absolute_url = request.build_absolute_uri(thumbnail_path) if thumbnail_path else ''

        return absolute_url
