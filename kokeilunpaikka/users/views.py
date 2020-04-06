from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..docs.mixins import ApiResponseCodeDocumentationMixin
from ..utils.pagination import ControllablePageNumberPagination
from .models import UserLookingForOption, UserStatusOption
from .serializers import (
    UserCreateSerializer,
    UserListSerializer,
    UserLookingForOptionSerializer,
    UserRetrieveSerializer,
    UserStatusOptionSerializer
)

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password')
)


class UserViewSet(
    ApiResponseCodeDocumentationMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """API endpoints for viewing user instances.

    list:
    Return a list of all user instances.

    ### Notices

    - Pagination may be used by giving the `page_size` query parameter.
    - A special response without the `image_url` field can be achieved by
      giving an extra `simplified` query parameter in the URL like
      `http://localhost:8019/api/users/?simplified`. This is useful when you
      need to fetch the whole list without pagination as it makes the query
      much more performant.

    ### Response

    Sample JSON response body:

        [
            {
                "id": 1,
                "first_name": "John",
                "full_name": "John Doe",
                "image_url": "http://testserver/media/test.jpeg",
                "last_name": "Doe"
            }
        ]

    create:
    Create a new user instance (registration).

    ### Request

    Sample JSON request body:

        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "password"
        }

    ### Response

        See the sample response of `retrieve` method.

    retrieve:
    Return the given user.

    ### Notices

    - `email` field is listed only if the user has defined so. This is handled
      through the `expose_email_address` field of user profile.

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "description": "Lorem ipsum",
            "email": "john.doe@example.com",
            "facebook_url": "https://facebook.com/kokeilunpaikka",
            "first_name": "John",
            "full_name": "John Doe",
            "image_url": "http://testserver/media/test.jpeg",
            "instagram_url": "https://instagram.com/kokeilunpaikka",
            "interested_in_themes": [
                {
                    "id": 1,
                    "is_curated": False,
                    "name": "Theme"
                }
            ],
            "last_name": "Doe",
            "linkedin_url": "",
            "looking_for": [
                {
                    "id": 1,
                    "value": "Help"
                }
            ],
            "twitter_url": "https://twitter.com/kokeilunpaikka"
        }

    looking_for_options:
    Return a list of options for things that users can select to their profiles
    to represent their points of interest. These options can be used while
    editing the user profile, see the `looking_for_ids` field.

    ### Response

    Sample JSON response body:

        [
            {
                "id": 1,
                "value": "Help"
            }
        ]
        }

    status_options:
    Return a list of options for statuses that users can select as their
    status. These options can be used while editing the user profile, see the
    `status_id` field.

    ### Response

    Sample JSON response body:

        [
            {
                "id": 1,
                "value": "Student"
            }
        ]

    """
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    ordering = ('-date_joined')
    pagination_class = ControllablePageNumberPagination
    search_fields = (
        'first_name',
        'last_name',
    )

    queryset = (
        get_user_model().objects
        .filter(
            is_active=True,
            profile__isnull=False,
        )
        .select_related('profile', 'profile__image')
    )

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_response_codes(self):
        if self.action == 'looking_for_options':
            return ('200',)
        if self.action == 'status_options':
            return ('200',)
        return super().get_response_codes()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserRetrieveSerializer
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'looking_for_options':
            return UserLookingForOptionSerializer
        if self.action == 'status_options':
            return UserStatusOptionSerializer

    @action(detail=False)
    def looking_for_options(self, request):
        serializer = self.get_serializer(
            UserLookingForOption.objects.all(),
            many=True
        )
        return Response(serializer.data)

    @action(detail=False)
    def status_options(self, request):
        serializer = self.get_serializer(
            UserStatusOption.objects.all(),
            many=True
        )
        return Response(serializer.data)
