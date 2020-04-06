from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets

from ..docs.mixins import ApiResponseCodeDocumentationMixin
from ..utils.permissions import ReadOnly
from .models import Question, Stage
from .serializers import QuestionSerializer, StageSerializer


class StageViewSet(
    ApiResponseCodeDocumentationMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """API endpoints for handling stage instances.

    list:
    Return a list of all stage instances.

    ### Response

    Sample JSON response body:

        [
            {
                "description": "Lorem ipsum",
                "name": "First phase",
                "stage_number": 1
            }
        ]

    retrieve:
    Return the given stage.

    ### Response

    Sample JSON response body:

        {
            "description": "Lorem ipsum",
            "name": "First phase",
            "stage_number": 1
        }

    """
    permission_classes = (
        ReadOnly,
    )
    queryset = Stage.objects.all()
    serializer_class = StageSerializer


class QuestionViewSet(
    ApiResponseCodeDocumentationMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """API endpoints for handling question instances.

    list:
    Return a list of all question instances related to the given stage.

    Returned list contains all questions for the stage existing in the system.
    This includes all questions targeted to different experiment challenges.
    That's why you probably don't want to fetch the whole list but use some kind
    of filtering instead. This can be done by giving query parameters to the
    request for filtering as described below.

    ### Filtering

    - Questions can be filtered based on possible relation to an experiment
      challenge. For example, following request URLs are supported:

        - Get all questions of stage 1 which should be presented only if the
        experiment is accepted to the experiment challenge (id 1):
        `/api/stages/1/questions/?experiment_challenge_id=1`

        - Get all questions of stage 1 which should be presented for every
        experiment regardless of any relation to experiment challenges:
        `/api/stages/1/questions/?experiment_challenge_id__isnull=true`

    ### Response

    Sample JSON response body:

        [
            {
                "id": 1,
                "description": "Lorem ipsum.",
                "experiment_challenge_id": 1,
                "is_public": true,
                "question": "Question to be asked",
            }
        ]

    retrieve:
    Return the given question.

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "description": "Lorem ipsum.",
            "experiment_challenge_id": 1,
            "is_public": true,
            "question": "Question to be asked",
        }

    """
    permission_classes = (
        permissions.IsAuthenticated,
    )
    serializer_class = QuestionSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = {
        'experiment_challenge_id': ['exact', 'isnull'],
    }

    def get_queryset(self):
        return Question.objects.filter(stage_id=self.kwargs['stage_id'])
