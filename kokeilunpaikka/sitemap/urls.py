from django.urls import include, path

from rest_framework import routers

from .views import EditableTextViewset, SiteConfigurationViewset

router = routers.DefaultRouter()
router.register('editable-text', EditableTextViewset, basename='editable-text')
router.register('configuration', SiteConfigurationViewset, basename='configuration')

urlpatterns = [
    path('', include(router.urls)),
]
