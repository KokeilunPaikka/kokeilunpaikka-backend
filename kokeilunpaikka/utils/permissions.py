from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReadOnly(BasePermission):
    """Permission to allow read access only."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class CreateOnly(BasePermission):
    """Permission to allow create access only.

    This assumes generic API views are used for the endpoint.
    """

    def has_permission(self, request, view):
        return (
            view.action == 'create'
        )


class IsAuthenticatedAndCreateOnly(permissions.IsAuthenticated):
    """Permission to allow create access for authenticated users.

    This assumes generic API views are used for the endpoint.
    """

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and
            view.action == 'create'
        )


class IsResponsibleAndDestroyOnly(permissions.IsAuthenticated):
    """Permission to only allow removal of an object for responsible users of
    the object.

    Method `get_object` of the view is called to make sure a single instance is
    accessed.

    Assumes the instance has an `is_responsible` method and generic API views
    are used for the endpoint.
    """

    def has_permission(self, request, view):
        try:
            instance = view.get_object()
        except AssertionError:
            return False

        return (
            super().has_permission(request, view) and
            view.action == 'destroy' and
            instance.is_responsible(request.user)
        )


class IsOwner(permissions.IsAuthenticated):
    """Permission to only allow owners of an object to access it.

    Method `get_object` of the view is called to make sure a single instance is
    accessed.

    Assumes the instance has an `is_owner` method.
    """

    def has_permission(self, request, view):
        try:
            instance = view.get_object()
        except AssertionError:
            return False

        return (
            super().has_permission(request, view) and
            instance.is_owner(request.user)
        )


class IsResponsible(permissions.IsAuthenticated):
    """Permission to only allow responsible users of an object to access it.

    Method `get_object` of the view is called to make sure a single instance is
    accessed. In case the instance can't be accessed and the resource is
    nested, custom `get_parent_object` view method is called too.

    Assumes the instance has an `is_responsible` method.
    """

    def has_permission(self, request, view):
        try:
            instance = view.get_object()
        except AssertionError:
            try:
                instance = view.get_parent_object()
            except AttributeError:
                return False

        return (
            super().has_permission(request, view) and
            instance.is_responsible(request.user)
        )
