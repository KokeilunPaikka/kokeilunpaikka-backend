from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields

from ..utils.models import TimeStampedModel


class UserProfile(TimeStampedModel):
    description = models.TextField(
        blank=True,
        verbose_name=_('description'),
    )
    expose_email_address = models.BooleanField(
        default=False,
        verbose_name=_('expose email address'),
        help_text=_(
            'Controls whether the email address is returned by the API and '
            'displayed in the user profile.'
        )
    )
    image = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        to='uploads.Image',
        verbose_name=_('image'),
    )
    interested_in_themes = models.ManyToManyField(
        blank=True,
        to='themes.Theme',
        verbose_name=_('interested in themes'),
    )
    language = models.CharField(
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        max_length=2,
        verbose_name=_('language'),
    )
    looking_for = models.ManyToManyField(
        blank=True,
        to='users.UserLookingForOption',
        verbose_name=_('looking for'),
    )
    offering = models.ManyToManyField(
        blank=True,
        to='users.UserLookingForOption',
        verbose_name=_('offering'),
        related_name='offering_userprofile_set'
    )
    status = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        to='users.UserStatusOption',
        verbose_name=_('user status option')
    )
    send_experiment_notification = models.BooleanField(
        verbose_name=_('send experiment notification'),
        default=False
    )
    user = models.OneToOneField(
        on_delete=models.CASCADE,
        related_name='profile',
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('user'),
    )

    # Social media links
    facebook_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Facebook account URL'),
    )
    instagram_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Instagram account URL'),
    )
    linkedin_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('LinkedIn account URL'),
    )
    twitter_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Twitter account URL'),
    )

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return _(
            'Profile for user "{}"'
        ).format(
            self.user
        )


class UserLookingForOption(TimeStampedModel, TranslatableModel):
    """Editable options (by superadmin) for things user is looking for in the
    service.
    """
    translations = TranslatedFields(
        value=models.CharField(
            help_text=_(
                'An option user can select for things he or she is looking '
                'for in the service.'
            ),
            max_length=255,
            verbose_name=_('value'),
        ),
        offering_value=models.CharField(
            help_text=_(
                'An alternative for value, used in what the user can offer'
            ),
            max_length=255,
            verbose_name=_('offering value'),
            default='',
            blank=True
        ),
    )

    class Meta:
        verbose_name = _('user looking for option')
        verbose_name_plural = _('user looking for options')

    def __str__(self):
        return self.value


class UserStatusOption(TimeStampedModel, TranslatableModel):
    """Editable options (by superadmin) for describing the status of user,
    like "student" or so on.
    """
    translations = TranslatedFields(
        value=models.CharField(
            help_text=_(
                'An option user can select for his/her status. Like student '
                'etc.'
            ),
            max_length=255,
            verbose_name=_('value'),
        )
    )

    class Meta:
        verbose_name = _('user status option')
        verbose_name_plural = _('user status options')

    def __str__(self):
        return self.value
