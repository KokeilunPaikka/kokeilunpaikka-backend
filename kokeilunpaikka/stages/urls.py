from django.urls import include, path

from rest_framework import routers

from .views import QuestionViewSet, StageViewSet

router = routers.DefaultRouter()
router.register('stages', StageViewSet, basename='stage')

question_router = routers.DefaultRouter()
question_router.register('questions', QuestionViewSet, basename='question')

urlpatterns = [
    path('', include(router.urls)),
    path('stages/<int:stage_id>/', include(question_router.urls)),
]
