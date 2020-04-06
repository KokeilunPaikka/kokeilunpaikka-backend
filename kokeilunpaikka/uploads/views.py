from PIL import Image as PILImage
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from ..docs.mixins import ApiResponseCodeDocumentationMixin
from ..utils.parsers import ImageUploadParser
from .models import Image
from .serializers import ImageSerializer


class ImageUploadViewSet(
    ApiResponseCodeDocumentationMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """API endpoints for handling image uploads.

    create:
    Create a new image instance through file upload.

    ### Permissions

    - Only allowed for authenticated users.

    ### Request

    Request with the image data in the request body is excepted. This could be
    considered more RESTful method than requests of type `multipart/form-data`
    which are not accepted.

    #### Following HTTP headers must be set:
    - **Content-Type**. Set to the MIME media type of the object being
      uploaded. The value should match the pattern `image/*`.
    - **Content-Disposition**. Client needs to signal the content filename to
      the service.

    #### Notices:

    - Supported image file types can be found here:
      <https://pillow.readthedocs.io/en/latest/handbook/image-file-formats.html>

    Sample request headers:

        Authorization: Token 8ade4e2acr2a7cvd94a5dd487x94cddd5q96aarf
        Content-Disposition: attachment; filename=image.jpg
        Content-Type: image/jpeg

    Sample request body:

        [IMAGE_DATA]

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "url": "http://localhost/media/untitled_KIeTzpa.png"
        }

    """
    parser_classes = (
        ImageUploadParser,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def create(self, request, *args, **kwargs):
        # Parse the file
        if 'file' not in request.data:
            raise ParseError('No file content was found.')
        file = request.data['file']

        # Verify the file is an image file
        try:
            img = PILImage.open(file)
            img.verify()
        except Exception:
            raise ParseError('Unsupported image type')

        # Save the file as image upload
        image = Image.objects.create(
            image=request.data['file'],
            uploaded_by=request.user
        )

        serializer = ImageSerializer(
            instance=image,
            context=self.get_serializer_context()
        )
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == 'create':
            # We return an empty serializer to remove the fields from the
            # schema for this action/endpoint.
            return serializers.Serializer
        return self.serializer_class
