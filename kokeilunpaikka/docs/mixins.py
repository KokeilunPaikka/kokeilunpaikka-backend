from .schemas import SchemaWithResponseFields


class ApiResponseCodeDocumentationMixin:
    """Adds response code documentation to Django REST Framework docs."""
    schema = SchemaWithResponseFields()

    def get_response_codes(self):
        if self.action == 'list':
            return ('200',)
        if self.action == 'create':
            return ('201', '400')
        if self.action == 'retrieve':
            return ('200', '404')
        if self.action == 'update':
            return ('200', '400', '404')
        if self.action == 'partial_update':
            return ('200', '400', '404')
        if self.action == 'destroy':
            return ('204', '404')
        return None
