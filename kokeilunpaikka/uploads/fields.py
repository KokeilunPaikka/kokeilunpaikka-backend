from rest_framework import serializers


class UploaderFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        if not request or not queryset:
            return queryset.none()
        return queryset.filter(uploaded_by=request.user)
