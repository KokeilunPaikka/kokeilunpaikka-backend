from django.urls import include, path

from rest_framework import routers

from .views import (
    ExperimentChallengeViewSet,
    ExperimentPostCommentViewSet,
    ExperimentPostViewSet,
    ExperimentViewSet
)

router = routers.DefaultRouter()
router.register('experiments', ExperimentViewSet, basename='experiment')
router.register(
    'experiment_challenges', ExperimentChallengeViewSet, basename='experiment-challenge')

experiment_post_router = routers.DefaultRouter()
experiment_post_router.register('posts', ExperimentPostViewSet, basename='experiment-post')

experiment_post_comment_router = routers.DefaultRouter()
experiment_post_comment_router.register(
    'comments', ExperimentPostCommentViewSet, basename='experiment-post-comment')

urlpatterns = [
    path('', include(router.urls)),
    path('experiments/<slug:experiment_slug>/', include(experiment_post_router.urls)),
    path('experiments/<slug:experiment_slug>/posts/<int:post_id>/', include(
        experiment_post_comment_router.urls
    )),
]
