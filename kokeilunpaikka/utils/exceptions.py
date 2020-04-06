from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework import exceptions
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Replace the default error representation with information from
    `get_full_details` method.

    This returns more verbose responses with error code information.
    """

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if response is not None:
        response.data = exc.get_full_details()

    return response
