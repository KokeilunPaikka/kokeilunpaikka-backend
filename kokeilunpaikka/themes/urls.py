from django.urls import include, path

from rest_framework import routers

from .views import ThemeViewSet

router = routers.DefaultRouter()
router.register('themes', ThemeViewSet, basename='theme')

urlpatterns = [
    path('', include(router.urls)),
]
