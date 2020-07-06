import logging
import os

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from extensions.mailer.mailer import send_template_mail

from .email_pool import ExperimentEmailThread
from ..stages.models import Question, QuestionAnswer, Stage
from ..stages.serializers import StageSerializer
from ..themes.models import Theme
from ..themes.serializers import ThemeSerializer
from ..uploads.models import Image
from ..utils.serializers import ThumbnailImageField
from ..users.models import UserProfile
from .models import (
    Experiment,
    ExperimentChallenge,
    ExperimentChallengeMembership,
    ExperimentChallengeTimelineEntry,
    ExperimentLookingForOption,
    ExperimentPost,
    ExperimentPostComment
)

logger = logging.getLogger(__name__)


class CreatorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')
    image_url = ThumbnailImageField(
        default=None,
        size='small_profile_image',
        source='profile.image.image',
    )

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'full_name',
            'image_url',
        )

    def to_representation(self, instance):
        # Make sure appropriate default values are returned for dot source
        # fields in the name of uniformity.
        data = super().to_representation(instance)
        if data['image_url'] is None:
            data['image_url'] = ''
        return data


class ExperimentLookingForOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExperimentLookingForOption
        fields = (
            'id',
            'value',
        )


class ExperimentChallengeTimelineEntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = ExperimentChallengeTimelineEntry
        fields = (
            'id',
            'content',
            'created_at',
            'date',
        )


class ExperimentChallengeMembershipSerializer(serializers.ModelSerializer):
    image_url = ThumbnailImageField(
        default=None,
        size='list_image',
        source='experiment.image.image',
    )
    is_published = serializers.BooleanField(
        source='experiment.is_published',
    )
    name = serializers.CharField(
        source='experiment.name',
    )
    published_at = serializers.DateTimeField(
        source='experiment.published_at',
    )
    short_description = serializers.CharField(
        source='experiment.short_description',
    )
    slug = serializers.SlugField(
        source='experiment.slug'
    )
    stage = StageSerializer(
        source='experiment.stage',
    )

    class Meta:
        model = ExperimentChallengeMembership
        fields = (
            'image_url',
            'is_approved',
            'is_published',
            'name',
            'published_at',
            'short_description',
            'slug',
            'stage',
        )

    def to_representation(self, instance):
        # Make sure appropriate default values are returned for dot source
        # fields in the name of uniformity.
        data = super().to_representation(instance)
        if data['image_url'] is None:
            data['image_url'] = ''
        return data


class ExperimentChallengeBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentChallenge
        fields = (
            'id',
            'ends_at',
            'name',
            'slug',
            'starts_at',
        )


class ExperimentChallengeBaseSerializer(serializers.ModelSerializer):
    image_url = ThumbnailImageField(
        size='list_image',
        source='image',
    )
    theme_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Theme.objects.all(),
        source='themes',
    )

    class Meta:
        model = ExperimentChallenge
        fields = (
            'id',
            'description',
            'ends_at',
            'image_url',
            'is_active',
            'lead_text',
            'name',
            'slug',
            'starts_at',
            'theme_ids',
        )

    def to_representation(self, instance):
        # Make sure appropriate default values are returned for dot source
        # fields in the name of uniformity.
        data = super().to_representation(instance)
        if data['image_url'] is None:
            data['image_url'] = ''
        return data


class ExperimentChallengeListSerializer(ExperimentChallengeBaseSerializer):
    pass


class ExperimentChallengeRetrieveSerializer(ExperimentChallengeBaseSerializer):
    experiments = ExperimentChallengeMembershipSerializer(
        many=True,
        source='experimentchallengemembership_set'
    )
    image_url = ThumbnailImageField(
        size='hero_image',
        source='image',
    )
    timeline_entries = ExperimentChallengeTimelineEntrySerializer(
        many=True,
        source='experimentchallengetimelineentry_set'
    )

    class Meta(ExperimentChallengeBaseSerializer.Meta):
        fields = ExperimentChallengeBaseSerializer.Meta.fields + (
            'experiments',
            'timeline_entries',
        )


class ExperimentPostCommentSerializer(serializers.ModelSerializer):
    created_by = CreatorSerializer(
        read_only=True,
    )

    class Meta:
        model = ExperimentPostComment
        fields = (
            'id',
            'content',
            'created_at',
            'created_by',
        )


class ExperimentPostSerializer(serializers.ModelSerializer):
    comments = ExperimentPostCommentSerializer(
        many=True,
        read_only=True,
    )
    created_by = CreatorSerializer(
        read_only=True,
    )
    image_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Image.objects.all(),
        required=False,
        source='images',
    )

    class Meta:
        model = ExperimentPost
        fields = (
            'id',
            'comments',
            'content',
            'count_of_comments',
            'created_at',
            'created_by',
            'image_ids',
            'title',
        )

    def to_representation(self, instance):
        """Replace the representation of images to contain URL as well as id to
        the file resource.
        """
        representation = super().to_representation(instance)
        representation.pop('image_ids')
        representation['images'] = ExperimentPostImageSerializer(
            context=self.context,
            instance=instance.images,
            many=True,
        ).data
        return representation


class ExperimentQuestionAnswerSerializer(serializers.ModelSerializer):
    stage_id = serializers.PrimaryKeyRelatedField(
        queryset=Stage.objects.all(),
        source='question.stage',
    )
    question = serializers.CharField(
        source='question.question'
    )

    class Meta:
        model = QuestionAnswer
        fields = (
            'id',
            'value',
            'question',
            'question_id',
            'stage_id',
        )


class ExperimentRetrieveSerializer(serializers.ModelSerializer):
    experiment_challenges = ExperimentChallengeBasicSerializer(
        many=True,
    )
    image_url = ThumbnailImageField(
        default=None,
        size='square_detail_image',
        source='image.image',
    )
    looking_for = ExperimentLookingForOptionSerializer(
        many=True,
    )
    posts = ExperimentPostSerializer(
        many=True
    )
    question_answers = serializers.SerializerMethodField()
    responsible_users = CreatorSerializer(
        many=True,
    )
    stage = StageSerializer()
    themes = ThemeSerializer(
        many=True,
    )

    class Meta:
        model = Experiment
        fields = (
            'id',
            'description',
            'experiment_challenges',
            'image_url',
            'is_published',
            'looking_for',
            'name',
            'organizer',
            'posts',
            'published_at',
            'question_answers',
            'responsible_users',
            'slug',
            'stage',
            'themes',
        )

    def get_question_answers(self, instance):
        stage = instance.stage
        answers = instance.questionanswer_set.all()
        if instance.experiment_challenges.count() > 0:
            answers = answers.exclude(
                question__ignore_in_experiment_challenge__in=instance.experiment_challenges.all()
            )
        serializer = ExperimentQuestionAnswerSerializer(
            answers,
            many=True
        )
        answer_data = serializer.data
        user = self.context.get('user')
        if user and user not in instance.responsible_users.all():
            return answer_data

        unanswered_questions = Question.objects.filter(
            stage__stage_number__lte=stage.stage_number,
            experiment_challenge_id__isnull=True,
            is_public=True
        ).exclude(questionanswer__in=answers).distinct()
        if instance.experiment_challenges.count() > 0:
            unanswered_questions = unanswered_questions.exclude(
                ignore_in_experiment_challenge__in=instance.experiment_challenges.all()
            )
            unanswered_challenge_questions = Question.objects.filter(
                experiment_challenge__in=instance.experiment_challenges.all()
            ).exclude(questionanswer__in=answers)
            for question in unanswered_challenge_questions:
                answer_data.append({
                    "id": f'{question.id}_unanswered',
                    "question": question.question,
                    "question_id": question.id,
                    "stage_id": question.stage.pk,
                    "value": ''
                })
        for question in unanswered_questions:
            answer_data.append({
                "id": f'{question.id}_unanswered',
                "question": question.question,
                "question_id": question.id,
                "stage_id": question.stage.pk,
                "value": ''
            })
        answer_data = sorted(answer_data, key=lambda x: x['question_id'])
        return answer_data

    def to_representation(self, instance):
        # Make sure appropriate default values are returned for dot source
        # fields in the name of uniformity.
        data = super().to_representation(instance)
        if data['image_url'] is None:
            data['image_url'] = ''
        return data


class ExperimentListSerializer(serializers.ModelSerializer):
    image_url = ThumbnailImageField(
        default=None,
        size='list_image',
        source='image.image',
    )
    themes = ThemeSerializer(
        many=True,
    )
    stage = StageSerializer()

    class Meta:
        model = Experiment
        fields = (
            'id',
            'image_url',
            'is_published',
            'name',
            'published_at',
            'short_description',
            'slug',
            'stage',
            'themes'
        )

    def to_representation(self, instance):
        # Make sure appropriate default values are returned for dot source
        # fields in the name of uniformity.
        data = super().to_representation(instance)
        if data['image_url'] is None:
            data['image_url'] = ''
        return data


class ExperimentSerializer(serializers.ModelSerializer):
    experiment_challenge_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ExperimentChallenge.objects.active().all(),
        required=False,
        source='experiment_challenges',
    )
    image_id = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.all(),
        required=False,
        source='image',
    )
    looking_for_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ExperimentLookingForOption.objects.all(),
        required=False,
        source='looking_for',
        write_only=True,
    )
    responsible_user_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=get_user_model().objects.all(),
        required=False,
        source='responsible_users',
    )
    stage_number = serializers.PrimaryKeyRelatedField(
        queryset=Stage.objects.all(),
        required=False,
        source='stage',
    )
    theme_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Theme.objects.all(),
        required=False,
        source='themes',
    )

    class Meta:
        model = Experiment
        fields = (
            'id',
            'description',
            'experiment_challenge_ids',
            'image_id',
            'is_published',
            'looking_for_ids',
            'name',
            'organizer',
            'responsible_user_ids',
            'slug',
            'stage_number',
            'success_rating',
            'theme_ids',
        )
        read_only_fields = (
            'slug',
        )
        extra_kwargs = {
            'success_rating': {'write_only': True},
        }

    def create(self, validated_data):
        """Create a new instance and make sure the user executing the addition
        is added as one of the responsible users for the experiment.
        """
        current_user_id = self.context['request'].user.id
        validated_data.setdefault('responsible_users', [])

        if current_user_id not in validated_data['responsible_users']:
            validated_data['responsible_users'].append(current_user_id)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Send notification to the newly added responsible user, in case
        the responsible_users field was changed.
        """
        if 'responsible_users' in validated_data:
            resp_users = instance.responsible_users.all()
            for user in validated_data['responsible_users']:
                if user not in resp_users:
                    mail_sent = send_template_mail(
                        recipient=user.email,
                        subject=_('You have been added to an experiment'),
                        template='experiment_user_add_notification',
                        variables={
                            "user": self.context['request'].user.get_full_name(),
                            "experiment_name": instance.name,
                            "profile_url":
                                f'{os.environ.get("BASE_FRONTEND_URL")}?login-to-profile=true'
                        }
                    )
                    if not mail_sent:
                        logger.error(
                            'Could not send responsible user add notification email for user '
                            'id %s.',
                            user.id
                        )

        if not instance.is_published and validated_data.get('is_published') is True:
            send_to = []
            themes = instance.themes.all()
            for user in UserProfile.objects.filter(send_experiment_notification=True).exclude(
                user__in=instance.responsible_users.all()
            ):
                user_themes = user.interested_in_themes.all()
                for theme in themes:
                    if theme in user_themes:
                        send_to.append(user.user.email)
            send_to = list(set(send_to))
            ExperimentEmailThread(send_to, instance.slug,
                                  self.context['request'].user.get_full_name()).start()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ExperimentRetrieveSerializer(
            instance,
            context=self.context
        ).to_representation(instance)

    def validate_responsible_user_ids(self, value):
        """Validate there's always at least one responsible for an experiment.

        The validation logic is run only for existing instances. All newly
        created instances have current user automatically set as one of the
        responsible users, see the `create` method above.
        """
        if self.instance and len(value) < 1:
            raise serializers.ValidationError(_(
                'There must always be at least one responsible user for an '
                'experiment.'
            ))
        return value

    def validate_stage_number(self, value):
        """Validate that stage_number must be 1 for newly created
        experiments.
        """
        if not self.instance and value.stage_number > 1:
            raise serializers.ValidationError(_(
                'Newly created experiment must be placed on the first stage.'
            ))
        return value


class ExperimentLookingForOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExperimentLookingForOption
        fields = (
            'id',
            'value',
        )


class ExperimentPostImageSerializer(serializers.ModelSerializer):
    url = ThumbnailImageField(
        size='post_image',
        source='image',
    )

    class Meta:
        model = Image
        fields = (
            'id',
            'url',
        )
