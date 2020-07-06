from .models import EditableText, SiteConfiguration
from .serializers import EditableTextSerializer, SiteConfigurationSerializer

from rest_framework import mixins, viewsets


class EditableTextViewset(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = EditableText.objects.all()
    serializer_class = EditableTextSerializer


class SiteConfigurationViewset(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = SiteConfiguration.objects.filter(active=True)
    serializer_class = SiteConfigurationSerializer
