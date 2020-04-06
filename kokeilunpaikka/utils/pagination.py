from rest_framework.pagination import CursorPagination, PageNumberPagination


class ControllableCursorPagination(CursorPagination):
    """Cursor pagination which client can control.

    Client can control the page size (number of results to return per page)
    using the `page_size` query parameter.

    `ordering` property must be defined in the view using this pagination
    class.
    """
    page_size_query_param = 'page_size'


class ControllablePageNumberPagination(PageNumberPagination):
    """PageNumberPagination which client can control.

    Client can control the page size (number of results to return per page)
    using the `page_size` query parameter.

    `ordering` property must be defined in the view using this pagination
    class.
    """
    page_size_query_param = 'page_size'
