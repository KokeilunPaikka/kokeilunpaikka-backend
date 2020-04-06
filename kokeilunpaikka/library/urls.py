from django.urls import include, path

from rest_framework import routers

from .views import LibraryItemViewSet

router = routers.DefaultRouter()
router.register('library_items', LibraryItemViewSet, basename='library-item')

urlpatterns = [
    path('', include(router.urls)),
]
