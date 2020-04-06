from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ..stages.models import QuestionAnswer, Stage
from ..stages.serializers import StageSerializer
from ..themes.models import Theme
from ..themes.serializers import ThemeSerializer
from ..uploads.models import Image
from ..utils.serializers import ThumbnailImageField
from .models import (
    Experiment,
    ExperimentChallenge,
    ExperimentChallengeMembership,
    ExperimentChallengeTimelineEntry,
    ExperimentLookingForOption,
    ExperimentPost,
    ExperimentPostComment
)


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
    question_answers = ExperimentQuestionAnswerSerializer(
        many=True,
        source='questionanswer_set'
    )
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
        """Validate that stage_number can't be increased if any of the
        experiment challenge memberships of the experiment is unapproved.
        """
        if not self.instance and value.stage_number > 1:
            raise serializers.ValidationError(_(
                'Newly created experiment must be placed on the first stage.'
            ))
        elif (
            self.instance and
            value.stage_number > 1 and
            self.instance.has_unapproved_challenge_memberships
        ):
            raise serializers.ValidationError(_(
                'The experiment is not approved to all selected experiment '
                'challenges and thus cannot be moved to the next stage.'
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
