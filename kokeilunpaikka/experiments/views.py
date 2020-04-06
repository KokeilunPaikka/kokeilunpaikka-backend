from django.contrib.auth import get_user_model
from django.db.models import Avg, Prefetch

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..docs.mixins import ApiResponseCodeDocumentationMixin
from ..stages.models import QuestionAnswer
from ..stages.serializers import QuestionAnswerSerializer
from ..themes.models import Theme
from ..utils.pagination import ControllablePageNumberPagination
from ..utils.permissions import (
    CreateOnly,
    IsAuthenticatedAndCreateOnly,
    IsOwner,
    IsResponsible,
    IsResponsibleAndDestroyOnly,
    ReadOnly
)
from .filters import ExperimentChallengeFilter, ExperimentFilter
from .models import (
    Experiment,
    ExperimentChallenge,
    ExperimentChallengeMembership,
    ExperimentLookingForOption,
    ExperimentPost,
    ExperimentPostComment
)
from .serializers import (
    ExperimentChallengeListSerializer,
    ExperimentChallengeRetrieveSerializer,
    ExperimentListSerializer,
    ExperimentLookingForOptionSerializer,
    ExperimentPostCommentSerializer,
    ExperimentPostSerializer,
    ExperimentRetrieveSerializer,
    ExperimentSerializer
)


class ExperimentChallengeViewSet(
    ApiResponseCodeDocumentationMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """View experiment challenges.

    list:
    Return a list of all experiment challenges.

    Results can be filtered by activity and theme ids and search against name
    values.

    Language of the returned content can be changed using `Accept-Language`
    header with a value of `fi`, `sv` or `en`.

    ### Response

    Sample JSON response body:

        [
            {
                "id": 1,
                "description": "<p>Lorem ipsum</p>",
                "ends_at": "2019-07-01T10:00:00Z",
                "image_url": "http://localhost/media/experiment_challenges/untitled.png",
                "is_active": True,
                "lead_text": "Lorem ipsum",
                "name": "Experiment Challenge",
                "slug": "experiment-challenge",
                "starts_at": "2019-07-10T18:00:00Z",
                "theme_ids": [
                    1,
                    2
                ]
            }
        ]

    retrieve:
    Return the given experiment challenge.

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "description": "<p>Lorem ipsum.</p>",
            "ends_at": "2019-07-01T10:00:00Z",
            "experiments": [
                {
                    "image_url": "http://localhost/media/untitled.png",
                    "is_approved": false,
                    "is_published": true,
                    "name": "Experiment",
                    "short_description": "Lorem ipsum.",
                    "slug": "experiment",
                    "stage_number": 1
                }
            ],
            "image_url": "http://localhost/media/experiment_challenges/untitled.png",
            "is_active": True,
            "lead_text": "Lorem ipsum.",
            "name": "Experiment Challenge",
            "slug": "experiment-challenge",
            "starts_at": "2019-07-10T18:00:00Z",
            "theme_ids": [
                1,
                2
            ],
            "timeline_entries": [
                {
                    "id": 1,
                    "content": "Content",
                    "created_at": "2019-07-10T12:00:00Z",
                    "date": "2019-07-10"
                }
            ]
        }

    """
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    ordering = ('-starts_at')
    filterset_class = ExperimentChallengeFilter
    lookup_field = 'translations__slug'
    pagination_class = ControllablePageNumberPagination
    search_fields = (
        'translations__name',
    )

    def get_queryset(self):
        """Queryset has to be declared in the `get_queryset` method to overcome
        caching issues related to current time while running multiple test
        cases.

        Experiments having a membership to an experiment challenge are filtered
        to active ones in the `retrieve` action. Experiments are visible only
        in the `retrieve` response, so there's no need to do the prefetching in
        any other actions.

        Note that we use the `active` method of the ExperimentQuerySet for
        retrieving action instead of `for_user` method. There's no need to show
        unpublished experiments for their resposible users in this endpoint.
        """
        if self.action == 'list':
            return ExperimentChallenge.objects.visible().prefetch_related(
                Prefetch(
                    'themes',
                    queryset=Theme.objects.all(),
                )
            )
        if self.action == 'retrieve':
            return ExperimentChallenge.objects.prefetch_related(
                Prefetch(
                    'experimentchallengemembership_set',
                    queryset=ExperimentChallengeMembership.objects.filter(
                        experiment_id__in=Experiment.objects.active()
                    ).order_by(
                        '-experiment__published_at',
                        '-experiment__created_at'
                    )
                )
            ).visible()

    def get_serializer_class(self):
        if self.action == 'list':
            return ExperimentChallengeListSerializer
        if self.action == 'retrieve':
            return ExperimentChallengeRetrieveSerializer


class ExperimentViewSet(
    ApiResponseCodeDocumentationMixin,
    viewsets.ModelViewSet
):
    """Handle experiments.

    list:
    Return a list of all published experiments.

    Results can be filtered by theme ids and search against name values.

    ### Notices

    - Pagination may be used by giving the `page_size` query parameter.

    ### Response

    Sample JSON response body:

        [
            {
                "id": 1,
                "image_url": "http://localhost/media/untitled.png",
                "is_published": true,
                "name": "Lorem ipsum",
                "published_at": "2019-07-10T12:00:00Z",
                "short_description": "Lorem ipsum",
                "slug": "lorem-ipsum",
                "stage": {
                    "description": "Lorem ipsum.",
                    "name": "First stage",
                    "stage_number": 1
                }
            }
        ]

    create:
    Create a new experiment instance.

    ### Notices

    - Current user is automatically assigned as one of the responsible users of
      the experiment.
    - All experiments must have at least one responsible user. Attempts to
      remove all responsible users cause an validation error.
    - By default all new experiments are set to be non-published.
    - Only public experiment challenges can given for
      `experiment_challenge_ids` field. This means challenges that have
      `is_visible` value set on and the current time withing the validity time
      range if set.

    ### Permissions

    - Only allowed for authenticated users.

    ### Request

    Sample JSON request body:

        {
            "description": "Lorem ipsum",
            "experiment_challenge_ids": [
                1
            ],
            "image_id": 1,
            "looking_for_ids": [
                1
            ],
            "name": "Lorem ipsum",
            "organizer": "Company Oy",
            "responsible_user_ids": [],
            "theme_ids": [
                1
            ]
        }

    ### Response

        See the response example of `retrieve` method.

    looking_for_options:
    Return a list of options for things that are tried to achieve by the
    experiment. These options can be used while creating a new experiment, see
    the `looking_for_ids` field.

    ### Response

    Sample JSON response body:

        [
            {
                "id": 1,
                "value": "Funding"
            }
        ]

    retrieve:
    Return the given (published) experiment.

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "description": "Lorem ipsum",
            "experiment_challenges": [
                {
                    "id": 1,
                    "ends_at": "2019-07-02T19:58:55Z",
                    "name": "Experiment Challenge",
                    "slug": "experiment-challenge",
                    "starts_at": "2019-07-01T15:53:54Z"
                }
            ],
            "image_url": "http://localhost/media/untitled.png",
            "is_published": true,
            "looking_for": [
                {
                    "id": 1,
                    "value": "Funding"
                }
            ],
            "name": "Lorem ipsum",
            "organizer": "Company Oy",
            "posts": [
                {
                    "id": 21,
                    "comments": [
                        {
                            "id": 1,
                            "content": "Comment content.",
                            "created_at": "2019-07-02T09:54:17.391279Z",
                            "created_by": {
                                "id": 1,
                                "full_name": "Petteri Testaa",
                                "image_url": "http://localhost/media/untitled.png"
                            }
                        }
                    ],
                    "content": "<p>Lorem ipsum.</p>",
                    "count_of_comments": 1,
                    "created_at": "2019-07-03T10:25:58.531608Z",
                    "created_by": {
                        "id": 1,
                        "full_name": "John Doe",
                        "image_url": "http://localhost/media/untitled.png"
                    },
                    "images": [
                        {
                            "id": 1,
                            "url": "http://localhost/media/untitled.png"
                        }
                    ],
                    "title": "Post"
                }
            ],
            "published_at": "2019-07-10T12:00:00Z",
            "question_answers": [
                {
                    "id": 1,
                    "question": "Question",
                    "question_id": 1,
                    "stage_id": 1,
                    "value": "My answer"
                }
            ],
            "responsible_users": [
                {
                    "full_name": "John Doe",
                    "id": 1,
                    "image_url": "http://localhost/media/untitled.png"
                }
            ],
            "slug": "lorem-ipsum",
            "stage": {
                "description": "Lorem ipsum.",
                "name": "First phase",
                "stage_number": 1
            },
            "themes": [
                {
                    "id": 1,
                    "is_curated": true,
                    "name": "My Theme"
                }
            ]
        }

    update:
    Update the given experiment.

    ### Notices

    - All experiments must have at least one responsible user. Attempts to
      remove all responsible users cause an validation error.
    - Only public experiment challenges can given for
      `experiment_challenge_ids` field. This means challenges that have
      `is_visible` value set on and the current time withing the validity time
      range if set.

    ### Permissions

    - Only allowed for responsible users of the experiment.

    ### Request

    Sample JSON request body:

        {
            "description": "Lorem ipsum",
            "experiment_challenge_ids": [
                1
            ],
            "image_id": null,
            "name": "Lorem ipsum",
            "responsible_user_ids": [
                1
            ],
            "success_rating": 8,
            "theme_ids": [
                1
            ]
        }

    ### Response

        See the response example of `retrieve` method.

    partial_update:
    Update partially the given experiment.

    ### Notices

    - All experiments must have at least one responsible user. Attempts to
      remove all responsible users cause an validation error.
    - Only public experiment challenges can given for
      `experiment_challenge_ids` field. This means challenges that have
      `is_visible` value set on and the current time withing the validity time
      range if set.

    ### Permissions

    - Only allowed for responsible users of the experiment.

    ### Request

    Sample JSON request body:

        {
            "is_published": true,
        }

    ### Response

        See the response example of `retrieve` method.

    destroy:
    Remove the given experiment.

    ### Permissions

    - Only allowed for responsible users of the experiment.

    answer_questions:
    Answer questions required for proceeding to the next stage.

    ### Notices

    - Questions needing to be answered can be fetched using
      `/api/stages/{stage_id}/questions/` endpoint.

    ### Permissions

    - Only allowed for responsible users of the experiment.

    ### Request

    Sample JSON request body:

        [
            {
                "question_id": 1,
                "value": "Answer 1"
            }
        ]

    ### Response

    No response content returned

    statistics:
    Return some statistical values based on existing experiments.

    ### Response

    Sample JSON response body:

        {
            "active_users_count": 284,
            "experiment_success_rating_average": 8.0,
            "users_with_experiments_count": 36,
            "visible_experiments_count": 29
        }

    """
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    ordering = ('-created_at')
    filterset_class = ExperimentFilter
    lookup_field = 'slug'
    pagination_class = ControllablePageNumberPagination
    permission_classes = (
        ReadOnly | IsAuthenticatedAndCreateOnly | IsResponsible,
    )
    search_fields = (
        'name',
    )
    serializer_class = ExperimentSerializer

    def get_queryset(self):
        return (
            Experiment.objects.for_user(self.request.user)
            .select_related('image', 'stage')
            .prefetch_related(
                Prefetch(
                    'questionanswer_set',
                    queryset=QuestionAnswer.objects.filter(
                        question__is_public=True
                    ).order_by(
                        'question_id'
                    )
                ),
                'experiment_challenges'
            ).order_by('-published_at', '-created_at')
        )

    def get_response_codes(self):
        if self.action == 'answer_questions':
            return ('204',)
        if self.action == 'looking_for_options':
            return ('200',)
        if self.action == 'statistics':
            return ('200',)
        return super().get_response_codes()

    def get_serializer_class(self):
        if self.action == 'answer_questions':
            return QuestionAnswerSerializer
        if self.action == 'looking_for_options':
            return ExperimentLookingForOptionSerializer
        if self.action == 'retrieve':
            return ExperimentRetrieveSerializer
        if self.action == 'list':
            return ExperimentListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False)
    def looking_for_options(self, request):
        serializer = self.get_serializer(
            ExperimentLookingForOption.objects.all(),
            many=True
        )
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def answer_questions(self, request, slug=None):
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            many=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def statistics(self, request):
        return Response({
            'active_users_count': (
                get_user_model().objects.filter(is_active=True).count()
            ),
            'experiment_success_rating_average': (
                Experiment.objects.aggregate(avg=Avg('success_rating'))['avg']
            ),
            'users_with_experiments_count': (
                get_user_model().objects.exclude(owned_experiments=None).count()
            ),
            'visible_experiments_count': Experiment.objects.active().count(),
        })


class ExperimentPostViewSet(
    ApiResponseCodeDocumentationMixin,
    viewsets.ModelViewSet
):
    """API endpoints for handling experiment post instances.

    list:
    Return a list of all experiment post instances.

    ### Response

    Sample JSON response body:

        [
            {
                "id": 1,
                "content": "<p>Lorem ipsum.</p>",
                "count_of_comments": 0,
                "created_at": "2019-07-02T09:54:17.386159Z",
                "created_by": {
                    "id": 1,
                    "full_name": "John Doe",
                    "image_url": "http://localhost/media/untitled.png"
                },
                "images": [
                    {
                        "id": 1,
                        "url": "http://localhost/media/untitled.png"
                    }
                ],
                "title": "New post"
            }
        ]

    create:
    Create a new experiment post instance.

    ### Permissions

    - Only allowed for responsible users of the experiment.

    ### Request

    Sample JSON request body:

        {
            "content": "<p>Lorem ipsum.</p>",
            "image_ids": [
                1
            ],
            "title": "New post"
        }

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "content": "<p>Lorem ipsum.</p>",
            "count_of_comments": 0,
            "created_at": "2019-07-02T09:54:17.386159Z",
            "created_by": {
                "id": 1,
                "full_name": "John Doe",
                "image_url": "http://localhost/media/untitled.png"
            },
            "images": [
                {
                    "id": 1,
                    "url": "http://localhost/media/untitled.png"
                }
            ],
            "title": "New post"
        }

    retrieve:
    Return the given experiment post.

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "content": "<p>Lorem ipsum.</p>",
            "count_of_comments": 0,
            "created_at": "2019-07-02T09:54:17.386159Z",
            "created_by": {
                "id": 1,
                "full_name": "John Doe",
                "image_url": "http://localhost/media/untitled.png"
            },
            "images": [
                {
                    "id": 1,
                    "url": "http://localhost/media/untitled.png"
                }
            ],
            "title": "New post"
        }

    update:
    Update the given experiment post.

    ### Permissions

    - Only allowed for responsible users of the experiment of the experiment
      post.

    ### Request

    Sample JSON request body:

        {
            "content": "<p>Lorem ipsum.</p>",
            "image_ids": [
                1
            ],
            "title": "New post"
        }

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "content": "<p>Lorem ipsum.</p>",
            "count_of_comments": 0,
            "created_at": "2019-07-02T09:54:17.386159Z",
            "created_by": {
                "id": 1,
                "full_name": "John Doe",
                "image_url": "http://localhost/media/untitled.png"
            },
            "images": [
                {
                    "id": 1,
                    "url": "http://localhost/media/untitled.png"
                }
            ],
            "title": "New post"
        }

    partial_update:
    Update partially the given experiment post.

    ### Permissions

    - Only allowed for responsible users of the experiment of the experiment
      post.

    ### Request

    Sample JSON request body:

        {
            "content": "<p>Lorem ipsum.</p>"
        }

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "content": "<p>Lorem ipsum.</p>",
            "count_of_comments": 0,
            "created_at": "2019-07-02T09:54:17.386159Z",
            "created_by": {
                "id": 1,
                "full_name": "John Doe",
                "image_url": "http://localhost/media/untitled.png"
            },
            "images": [
                {
                    "id": 1,
                    "url": "http://localhost/media/untitled.png"
                }
            ],
            "title": "New post"
        }

    destroy:
    Remove the given experiment post.

    ### Permissions

    - Only allowed for responsible users of the experiment of the experiment
      post.

    """
    permission_classes = (
        ReadOnly | IsResponsible,
    )
    serializer_class = ExperimentPostSerializer

    def get_parent_object(self):
        return Experiment.objects.get(slug=self.kwargs['experiment_slug'])

    def get_queryset(self):
        return ExperimentPost.objects.filter(
            experiment__slug=self.kwargs['experiment_slug'],
        )

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            experiment=Experiment.objects.get(slug=self.kwargs['experiment_slug']),
        )


class ExperimentPostCommentViewSet(
    ApiResponseCodeDocumentationMixin,
    viewsets.ModelViewSet
):
    """API endpoints for handling experiment post comment instances.

    list:
    Return a list of all experiment post comments.

    ### Response

    Sample JSON response body:

        [
            {
                "id": 1,
                "content": "Lorem ipsum.",
                "created_at": "2019-07-03T09:24:15.543223Z",
                "created_by": {
                    "full_name": "John Doe",
                    "id": 1,
                    "image_url": "http://localhost/media/untitled.png"
                }
            }
        ]

    create:
    Create a new experiment post comment instance.

    ### Permissions

    - No permissions needed. Unauthenticated users can also write comments.

    ### Request

    Sample JSON request body:

        {
            "content": "Lorem ipsum."
        }

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "content": "Lorem ipsum.",
            "created_at": "2019-07-03T09:24:15.543223Z",
            "created_by": {
                "full_name": "John Doe",
                "id": 1,
                "image_url": "http://localhost/media/untitled.png"
            }
        }

    retrieve:
    Return the given experiment post comment.

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "content": "Lorem ipsum.",
            "created_at": "2019-07-03T09:24:15.543223Z",
            "created_by": {
                "full_name": "John Doe",
                "id": 1,
                "image_url": "http://localhost/media/untitled.png"
            }
        }

    update:
    Update the given experiment post comment.

    ### Permissions

    - Only allowed for creator of the comment.

    ### Request

    Sample JSON request body:

        {
            "content": "Lorem ipsum."
        }

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "content": "Lorem ipsum.",
            "created_at": "2019-07-03T09:24:15.543223Z",
            "created_by": {
                "full_name": "John Doe",
                "id": 1,
                "image_url": "http://localhost/media/untitled.png"
            }
        }

    partial_update:
    Update partially the given experiment post comment.

    ### Permissions

    - Only allowed for creator of the comment.

    ### Request

    Sample JSON request body:

        {
            "content": "Lorem ipsum."
        }

    ### Response

    Sample JSON response body:

        {
            "id": 1,
            "content": "Lorem ipsum.",
            "created_at": "2019-07-03T09:24:15.543223Z",
            "created_by": {
                "full_name": "John Doe",
                "id": 1,
                "image_url": "http://localhost/media/untitled.png"
            }
        }

    destroy:
    Remove the given experiment post comment.

    ### Permissions

    - Only allowed for responsible users of the experiment or creator of the
      comment.

    """
    permission_classes = (
        ReadOnly | CreateOnly | IsResponsibleAndDestroyOnly | IsOwner,
    )
    queryset = ExperimentPostComment.objects.all()
    serializer_class = ExperimentPostCommentSerializer

    def get_queryset(self):
        return ExperimentPostComment.objects.filter(
            experiment_post_id=self.kwargs['post_id'],
            experiment_post__experiment__slug=self.kwargs['experiment_slug'],
        )

    def perform_create(self, serializer):
        kwargs = {
            'experiment_post_id': self.kwargs['post_id'],
        }

        if self.request.user.is_authenticated:
            kwargs['created_by'] = self.request.user

        serializer.save(**kwargs)
