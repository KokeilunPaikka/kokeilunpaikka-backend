from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ..experiments.models import Experiment
from ..experiments.serializers import ExperimentListSerializer
from ..themes.models import Theme
from ..themes.serializers import ThemeSerializer
from ..uploads.fields import UploaderFilteredPrimaryKeyRelatedField
from ..uploads.models import Image
from ..utils.serializers import ThumbnailImageField
from .models import UserLookingForOption, UserProfile, UserStatusOption


class UserLookingForOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLookingForOption
        fields = (
            'id',
            'value',
        )


class UserStatusOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserStatusOption
        fields = (
            'id',
            'value',
        )


class UserBaseSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        source='get_full_name',
        read_only=True,
    )

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'first_name',
            'full_name',
            'last_name',
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class UserListSerializer(UserBaseSerializer):
    image_url = ThumbnailImageField(
        size='list_image',
        source='profile.image.image',
        default=None,
    )

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + (
            'image_url',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add possibility to remove image_url field by using a custom URL
        # param.
        #
        # This is useful when loading the whole dataset without pagination as
        # the fetching of image information requires a lot of database queries
        # because of the limits of easy-thumbnails library.
        if 'simplified' in self.context['request'].GET:
            self.fields.pop('image_url')

    def to_representation(self, instance):
        # Make sure appropriate default values are returned for dot source
        # fields in the name of uniformity.
        data = super().to_representation(instance)
        if 'image_url' in data and data['image_url'] is None:
            data['image_url'] = ''
        return data

    def update(self, instance, validated_data):
        raise NotImplementedError('`update()` not allowed.')

    def create(self, validated_data):
        raise NotImplementedError('`create()` not allowed.')


class SingleUserBaseSerializer(UserBaseSerializer):
    description = serializers.CharField(
        source='profile.description',
        required=False,
    )
    experiments = serializers.SerializerMethodField()
    facebook_url = serializers.URLField(
        source='profile.facebook_url',
        required=False,
    )
    instagram_url = serializers.URLField(
        source='profile.instagram_url',
        required=False,
    )
    linkedin_url = serializers.URLField(
        source='profile.linkedin_url',
        required=False,
    )
    twitter_url = serializers.URLField(
        source='profile.twitter_url',
        required=False,
    )

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + (
            'description',
            'experiments',
            'facebook_url',
            'instagram_url',
            'linkedin_url',
            'twitter_url',
        )

    def get_experiments(self, obj):
        current_user_id = self.context['request'].user.id

        if current_user_id is None:
            qs = Experiment.objects.filter(
                is_published=True,
                responsible_users__id=obj.id
            )
        else:
            qs = Experiment.objects.filter(
                Q(is_published=True) |
                Q(responsible_users__id=current_user_id)
            ).filter(
                responsible_users__id=obj.id
            )

        return ExperimentListSerializer(
            qs.order_by('-published_at', '-created_at'),
            many=True,
            context=self.context
        ).data


class UserRetrieveSerializer(SingleUserBaseSerializer):
    image_url = ThumbnailImageField(
        size='square_detail_image',
        source='profile.image.image',
        default=None,
    )
    interested_in_themes = ThemeSerializer(
        many=True,
        source='profile.interested_in_themes',
    )
    looking_for = UserLookingForOptionSerializer(
        many=True,
        source='profile.looking_for',
    )

    class Meta(SingleUserBaseSerializer.Meta):
        fields = SingleUserBaseSerializer.Meta.fields + (
            'image_url',
            'interested_in_themes',
            'looking_for',
        )

    def to_representation(self, instance):
        # Make sure appropriate default values are returned for dot source
        # fields in the name of uniformity. This is an empty string for
        # CharField serializer and an empty list for ListSerializer.
        data = super().to_representation(instance)
        for field in (
            'description',
            'image_url',
            'facebook_url',
            'instagram_url',
            'linkedin_url',
            'twitter_url',
        ):
            if data[field] is None:
                data[field] = ''
        for field in ('interested_in_themes', 'looking_for'):
            if data[field] is None:
                data[field] = []
        if (
            hasattr(instance, 'profile') and
            instance.profile.expose_email_address is True
        ):
            data['email'] = instance.email
        return data

    def update(self, instance, validated_data):
        raise NotImplementedError('`update()` not allowed.')

    def create(self, validated_data):
        raise NotImplementedError('`create()` not allowed.')


class CurrentUserRetrieveSerializer(UserRetrieveSerializer):
    """Serializer to represent the data of the current user.

    Sensitive fields of the user which should be exposed only for the current
    user should be determined here.
    """
    expose_email_address = serializers.BooleanField(
        source='profile.expose_email_address',
    )
    status = UserStatusOptionSerializer(
        source='profile.status',
    )

    class Meta(UserRetrieveSerializer.Meta):
        fields = UserRetrieveSerializer.Meta.fields + (
            'email',
            'expose_email_address',
            'status',
        )
        extra_kwargs = {
            'email': {'read_only': True}
        }

    def to_representation(self, instance):
        # Make sure appropriate default values are returned for dot source
        # fields in the name of uniformity.
        data = super().to_representation(instance)
        if data['expose_email_address'] is None:
            data['expose_email_address'] = False
        return data


class UserUpdateSerializer(SingleUserBaseSerializer):
    expose_email_address = serializers.BooleanField(
        source='profile.expose_email_address',
        required=False,
    )
    image_id = UploaderFilteredPrimaryKeyRelatedField(
        queryset=Image.objects.all(),  # filtered to images uploaded by the user
        required=False,
        source='profile.image',
    )
    interested_in_theme_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Theme.objects.all(),
        required=False,
        source='profile.interested_in_themes',
    )
    language = serializers.ChoiceField(
        source='profile.language',
        choices=settings.LANGUAGES,
        required=False,
    )
    looking_for_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=UserLookingForOption.objects.all(),
        required=False,
        source='profile.looking_for',
    )
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=UserStatusOption.objects.all(),
        required=False,
        source='profile.status',
    )

    class Meta(SingleUserBaseSerializer.Meta):
        fields = SingleUserBaseSerializer.Meta.fields + (
            'expose_email_address',
            'image_id',
            'interested_in_theme_ids',
            'language',
            'looking_for_ids',
            'status_id',
        )

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for field in (
                'description',
                'expose_email_address',
                'image',
                'language',
                'status',
                'facebook_url',
                'instagram_url',
                'linkedin_url',
                'twitter_url',
            ):
                if field in profile_data:
                    setattr(profile, field, profile_data[field])
            if 'interested_in_themes' in profile_data:
                profile.interested_in_themes.set(profile_data['interested_in_themes'])
            if 'looking_for' in profile_data:
                profile.looking_for.set(profile_data['looking_for'])
            profile.save()
        return instance

    def create(self, validated_data):
        raise NotImplementedError('`create()` not allowed.')


class UserDetailsSerializer(UserUpdateSerializer):
    """Serializer provided as USER_DETAILS_SERIALIZER for django-rest-auth
    package.

    Uses the UserUpdateSerializer as is. The response is identical to
    CurrentUserRetrieveSerializer, see the `to_representation` method.
    """

    def to_representation(self, instance):
        return CurrentUserRetrieveSerializer(context=self.context).to_representation(instance)


class UserCreateSerializer(UserBaseSerializer):

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + (
            'email',
            'password',
        )
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def create(self, validated_data):
        with transaction.atomic():
            instance = get_user_model().objects.create_user(
                username=validated_data['email'],
                **validated_data
            )

            # Empty user profile is automatically created to signify the user
            # was created through the registration and process and should be
            # visible in the user listings.
            #
            # Note that the profile can also be added manually by the
            # superadmin and thus exposing those users to public.
            UserProfile.objects.create(
                user=instance,
            )

        instance.send_registration_notification()

        return instance

    def to_representation(self, instance):
        return UserRetrieveSerializer(context=self.context).to_representation(instance)

    def update(self, instance, validated_data):
        raise NotImplementedError('`update()` not allowed.')

    def validate_email(self, value):
        """Validate there isn't already a username with the given email
        address.

        Email address is used as an username for every new account created
        using this registration path.
        """
        if get_user_model().objects.filter(username=value).exists():
            raise serializers.ValidationError(_(
                'There is already an account with given email address.'
            ))
        return value
