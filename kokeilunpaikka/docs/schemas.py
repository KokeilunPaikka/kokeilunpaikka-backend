from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import AutoSchema


class SchemaWithResponseFields(AutoSchema):

    RESPONSE_CODES_WITH_DESCRIPTIONS = {
        '200': 'Request was successful.',
        '201': 'Resource was created successfully.',
        '204': 'Request was successful. No content returned.',
        '400': 'Validation error(s) occured.',
        '403': 'Permission denied.',
        '404': 'Resource was not found.',
    }

    def get_description_by_response_code(self, response_code):
        if response_code in self.RESPONSE_CODES_WITH_DESCRIPTIONS:
            return self.RESPONSE_CODES_WITH_DESCRIPTIONS[response_code]
        return None

    def get_manual_fields(self, path, method):
        """Add fields for response codes of the API endpoint."""
        extra_fields = []

        view_response_codes = self.view.get_response_codes()

        if view_response_codes:
            for response_code in view_response_codes:

                # Get description text
                description = self.get_description_by_response_code(
                    response_code
                )

                # Add field
                extra_fields.append(
                    coreapi.Field(
                        name=response_code,
                        location='response_codes',
                        schema=coreschema.String(
                            description=description
                        )
                    ),
                )

        # Get additional schema fields from the view if determined
        view_extra_fields = (
            self.view.get_schema_fields() if
            getattr(self.view, 'get_schema_fields', None) else
            []
        )

        manual_fields = super().get_manual_fields(path, method)

        return manual_fields + extra_fields + view_extra_fields
