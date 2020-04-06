from rest_framework import mixins, permissions, viewsets

from ..docs.mixins import ApiResponseCodeDocumentationMixin
from .models import Theme
from .serializers import ThemeSerializer


class ThemeViewSet(
    ApiResponseCodeDocumentationMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """API endpoints for handling theme instances.

    list:
    Return a list of all theme instances.

    Language of the returned content can be changed using `Accept-Language`
    header with a value of `fi`, `sv` or `en`.

    ### Response

    Sample JSON response body:

        [
            {
                "id": 1,
                "is_curated": false,
                "name": "My theme"
            }
        ]

    create:
    Create a new theme instance.

    ### Permissions

    - Only allowed for authenticated users.

    ### Request

    Sample JSON request body:

        {
            "name": "My theme"
        }

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "is_curated": false,
            "name": "My theme"
        }

    retrieve:
    Return the given theme.

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "is_curated": false,
            "name": "My theme"
        }

    """
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
