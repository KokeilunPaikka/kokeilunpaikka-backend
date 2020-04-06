from rest_framework import filters, mixins, viewsets

from ..docs.mixins import ApiResponseCodeDocumentationMixin
from ..utils.pagination import ControllablePageNumberPagination
from .models import LibraryItem
from .serializers import (
    LibraryItemListSerializer,
    LibraryItemRetrieveSerializer
)


class LibraryItemViewSet(
    ApiResponseCodeDocumentationMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """View library items.

    list:
    Return a list of all library items.

    Language of the returned content can be changed using `Accept-Language`
    header with a value of `fi`, `sv` or `en`.

    ### Response

    Sample JSON response body:

        [
            {
                "id": 1,
                "description": "<p>Lorem ipsum</p>",
                "image_url": "http://localhost/media/library_items/test.jpg.720x480_q80_crop.jpg",
                "lead_text": "Lorem ipsum",
                "name": "Example",
                "slug": "example"
            }
        ]

    retrieve:
    Return the given library item.

    ### Notices

    - Lists all public experiments that use themes linked to this library item.

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "description": "<p>Lorem ipsum</p>",
            "experiments": [
                {
                    "id": 1,
                    "image_url": "http://localhost/media/test.jpg.720x480_q80_crop.jpg",
                    "is_published": true,
                    "name": "Test",
                    "published_at": "2019-11-07T09:43:50.837027Z",
                    "short_description": "Lorem ipsum",
                    "slug": "test",
                    "stage": {
                        "description": "Lorem ipsum",
                        "name": "First stage",
                        "stage_number": 1
                    }
                }
            ],
            "image_url": "http://localhost/media/library_items/test.jpg.1280x460_q80_crop.jpg",
            "lead_text": "Lorem ipsum",
            "name": "Example",
            "slug": "example"
        }

    """
    filter_backends = (
        filters.OrderingFilter,
    )
    ordering = ('-created_at')
    lookup_field = 'translations__slug'
    pagination_class = ControllablePageNumberPagination

    def get_queryset(self):
        return LibraryItem.objects.visible()

    def get_serializer_class(self):
        if self.action == 'list':
            return LibraryItemListSerializer
        if self.action == 'retrieve':
            return LibraryItemRetrieveSerializer
