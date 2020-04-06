from django.urls import include, path

from rest_framework import routers

from .views import ImageUploadViewSet

router = routers.DefaultRouter()
router.register('images', ImageUploadViewSet, basename='image')

urlpatterns = [
    path('uploads/', include(router.urls)),
]
