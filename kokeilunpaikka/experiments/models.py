from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from parler.models import TranslatableModel, TranslatedFields

from ..stages.models import Stage
from ..utils.models import SanitizedRichTextField, TimeStampedModel
from .querysets import ExperimentChallengeQuerySet, ExperimentQuerySet


class ExperimentChallenge(TimeStampedModel, TranslatableModel):
    ends_at = models.DateTimeField(
        null=True,
        verbose_name=_('ends at'),
    )
    image = models.ImageField(
        upload_to='experiment_challenges/',
        verbose_name=_('image'),
    )
    is_visible = models.BooleanField(
        default=True,
        verbose_name=_('is visible'),
    )
    lead_text = models.TextField(
        blank=True,
        help_text=_(
            'Emphasized opening content of the challenge.'
        ),
        verbose_name=_('lead text'),
    )
    starts_at = models.DateTimeField(
        null=True,
        verbose_name=_('starts at'),
    )
    themes = models.ManyToManyField(
        blank=True,
        to='themes.Theme',
        verbose_name=_('themes'),
    )

    translations = TranslatedFields(
        description=SanitizedRichTextField(
            verbose_name=_('description'),
        ),
        name=models.CharField(
            max_length=255,
            verbose_name=_('name'),
        ),
        slug=models.SlugField(
            help_text=_(
                'Automatically generated user-friendly short text that is '
                'used in the URL shown in the address bar to identify and '
                'describe this resource.'
            ),
            max_length=255,
            unique=True,
            verbose_name=_('slug'),
        ),
    )

    objects = ExperimentChallengeQuerySet.as_manager()

    class Meta:
        verbose_name = _('experiment challenge')
        verbose_name_plural = _('experiment challenges')

    def __str__(self):
        return '{} ({} – {})'.format(
            self.name,
            self.starts_at,
            self.ends_at
        )

    @property
    def is_active(self):
        """Determines whether the experiment is visible to users."""
        now = timezone.now()
        return (
            self.is_visible and
            (self.starts_at is None or self.starts_at <= now) and
            (self.ends_at is None or self.ends_at >= now)
        )


class ExperimentChallengeMembership(TimeStampedModel):
    experiment = models.ForeignKey(
        on_delete=models.CASCADE,
        to='experiments.Experiment',
        verbose_name=_('experiment'),
    )
    experiment_challenge = models.ForeignKey(
        on_delete=models.CASCADE,
        to='experiments.ExperimentChallenge',
        verbose_name=_('experiment challenge'),
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('is approved'),
    )

    class Meta:
        unique_together = (
            'experiment',
            'experiment_challenge'
        )
        verbose_name = _('experiment challenge membership')
        verbose_name_plural = _('experiment challenge memberships')


class ExperimentChallengeTimelineEntry(TimeStampedModel):
    date = models.DateField(
        verbose_name=_('date'),
    )
    content = models.TextField(
        verbose_name=_('content'),
    )
    experiment_challenge = models.ForeignKey(
        on_delete=models.CASCADE,
        to='experiments.ExperimentChallenge',
        verbose_name=_('experiment challenge'),
    )

    class Meta:
        ordering = (
            'date',
            'created_at'
        )
        verbose_name = _('experiment challenge timeline entry')
        verbose_name_plural = _('experiment challenge timeline entries')


class Experiment(TimeStampedModel):
    created_by = models.ForeignKey(
        null=True,
        on_delete=models.SET_NULL,
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('created by'),
    )
    description = models.TextField(
        verbose_name=_('description'),
    )
    experiment_challenges = models.ManyToManyField(
        blank=True,
        through='experiments.ExperimentChallengeMembership',
        to='experiments.ExperimentChallenge',
        verbose_name=_('experiment challenges'),
    )
    image = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        to='uploads.Image',
        verbose_name=_('image'),
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('is published'),
    )
    language = models.CharField(
        # As of now, this not used anywhere but exists to store information
        # about the language used in the content based on the information found
        # during the data import from the old system.
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        max_length=2,
        verbose_name=_('language'),
    )
    looking_for = models.ManyToManyField(
        blank=True,
        help_text=_(
            'Options determining what kind of things are looked for the '
            'experiment in the service.'
        ),
        to='experiments.ExperimentLookingForOption',
        verbose_name=_('looking for'),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('name'),
    )
    organizer = models.CharField(
        blank=True,
        help_text=_(
            'Name of the person or organization organizing the experiment.'
        ),
        max_length=255,
        verbose_name=_('organizer'),
    )
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('published at'),
    )
    responsible_users = models.ManyToManyField(
        help_text=_(
            'Users who have full management permissions to this experiment.'
        ),
        related_name='owned_experiments',
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('responsible users'),
    )
    slug = AutoSlugField(
        blank=False,
        editable=True,
        help_text=_(
            'Automatically generated user-friendly short text that is '
            'used in the URL shown in the address bar to identify and '
            'describe this resource.'
        ),
        max_length=255,
        populate_from='name',
        unique=True,
        verbose_name=_('slug'),
    )
    stage = models.ForeignKey(
        default=Stage.get_initial_stage,
        help_text=_(
            'Current stage of the experiment.'
        ),
        on_delete=models.PROTECT,
        to='stages.Stage',
        verbose_name=_('stage'),
    )
    success_rating = models.IntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(10), MinValueValidator(1)],
        verbose_name=_('success rating'),
        help_text=_('Rating with a value from 1 to 10.')
    )
    themes = models.ManyToManyField(
        blank=True,
        to='themes.Theme',
        verbose_name=_('themes'),
    )

    objects = ExperimentQuerySet.as_manager()

    class Meta:
        verbose_name = _('experiment')
        verbose_name_plural = _('experiments')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.published_at is None and self.is_published is True:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def is_responsible(self, user):
        """Check if the given user is one of responsible users of this
        experiment.
        """
        return user in self.responsible_users.all()

    @property
    def short_description(self):
        return self.description[:200]

    @property
    def has_unapproved_challenge_memberships(self):
        return any([
            not m.is_approved for m in self.experimentchallengemembership_set.all()
        ])


class ExperimentPost(TimeStampedModel):
    content = SanitizedRichTextField(
        verbose_name=_('content'),
    )
    created_by = models.ForeignKey(
        null=True,
        on_delete=models.SET_NULL,
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('created by'),
    )
    experiment = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name='posts',
        to='experiments.Experiment',
        verbose_name=_('experiment'),
    )
    images = models.ManyToManyField(
        blank=True,
        to='uploads.Image',
        verbose_name=_('images'),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('name'),
    )

    class Meta:
        verbose_name = _('experiment post')
        verbose_name_plural = _('experiment posts')

    def __str__(self):
        return self.title

    @property
    def count_of_comments(self):
        return self.comments.count()
    count_of_comments.fget.short_description = _('count of comments')

    def is_responsible(self, user):
        """Check if the given user is one of responsible users of the
        experiment of this post.
        """
        return user in self.experiment.responsible_users.all()


class ExperimentPostComment(TimeStampedModel):
    content = models.TextField(
        verbose_name=_('content'),
    )
    created_by = models.ForeignKey(
        null=True,
        on_delete=models.SET_NULL,
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('created by'),
    )
    experiment_post = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name='comments',
        to='experiments.ExperimentPost',
        verbose_name=_('experiment post'),
    )

    class Meta:
        verbose_name = _('experiment post comment')
        verbose_name_plural = _('experiment post comments')

    def __str__(self):
        return _(
            'Comment for "{}" by {}'
        ).format(
            self.experiment_post,
            self.created_by,
        )

    def is_owner(self, user):
        return user == self.created_by

    def is_responsible(self, user):
        """Check if the given user is one of responsible users of the
        experiment of this post comment.
        """
        return user in self.experiment_post.experiment.responsible_users.all()


class ExperimentExternalLink(TimeStampedModel):
    url = models.URLField(
        verbose_name=_('External link (URL)'),
    )
    experiment = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name='external_links',
        to='experiments.Experiment',
        verbose_name=_('experiment'),
    )

    class Meta:
        verbose_name = _('experiment external link')
        verbose_name_plural = _('experiment external links')

    def __str__(self):
        return self.url


class ExperimentLookingForOption(TimeStampedModel, TranslatableModel):
    """Editable options (by superadmin) for things experiment is looking for in
    the service.
    """
    translations = TranslatedFields(
        value=models.CharField(
            max_length=255,
            verbose_name=_('value'),
        )
    )

    class Meta:
        verbose_name = _('experiment looking for option')
        verbose_name_plural = _('experiment looking for options')

    def __str__(self):
        return self.value
