from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields

from ..utils.models import TimeStampedModel


class Stage(TimeStampedModel, TranslatableModel):
    """Stage determines the current phase of an experiment in the experiment
    process."""
    stage_number = models.IntegerField(
        help_text=_(
            'Determines the stage of an experiment numerically. Numbers '
            'should be in the ascending order, largest number indicating the '
            'last stage of an experiment. Numbering should start from one (1).'
        ),
        primary_key=True,
        unique=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        verbose_name=_('stage number'),
    )

    translations = TranslatedFields(
        description=models.TextField(
            verbose_name=_('description'),
        ),
        name=models.CharField(
            max_length=255,
            verbose_name=_('name'),
        )
    )

    class Meta:
        verbose_name = _('stage')
        verbose_name_plural = _('stages')

    def __str__(self):
        return '{} ({})'.format(
            self.name,
            self.stage_number
        )

    @classmethod
    def get_initial_stage(cls):
        """Get instance of the first stage of the experiment process."""
        return cls.objects.filter(stage_number=1).first()


class Question(TimeStampedModel, TranslatableModel):
    experiment_challenge = models.ForeignKey(
        blank=True,
        help_text=_(
            'Question can be attached to a specific experiment challenge and '
            'thus is only asked if the experiment is attached for such '
            'challenge.'
        ),
        null=True,
        on_delete=models.CASCADE,
        to='experiments.ExperimentChallenge',
        verbose_name=_('experiment challenge'),
    )
    ignore_in_experiment_challenge = models.ManyToManyField(
        blank=True,
        help_text=_(
            'Questions can be marked to be ignored in case of an experiment '
            'challenge.'
        ),
        to='experiments.ExperimentChallenge',
        verbose_name=_('ignore in experiment challenge'),
        related_name="ignored_questions"
    )
    is_public = models.BooleanField(
        default=True,
        help_text=_(
            'Determines whether the question and the related answer is shown '
            'in the detail page of an experiment. Non-public questions can be '
            'used for gathering private background information.'
        ),
        verbose_name=_('is public'),
    )
    stage = models.ForeignKey(
        help_text=_(
            'Question should be presented when trying to proceed to this '
            'specific stage.'
        ),
        on_delete=models.PROTECT,
        to='stages.Stage',
        verbose_name=_('stage'),
    )

    translations = TranslatedFields(
        question=models.CharField(
            max_length=255,
            verbose_name=_('question'),
        ),
        description=models.TextField(
            verbose_name=_('description'),
            help_text=_(
                'Detailed instructions for answering the question. Visible as '
                'a placeholder text in the form field.'
            )
        )
    )

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')

    def __str__(self):
        return self.question


class QuestionAnswer(TimeStampedModel):
    answered_by = models.ForeignKey(
        null=True,
        on_delete=models.SET_NULL,
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('answered by'),
    )
    experiment = models.ForeignKey(
        on_delete=models.CASCADE,
        to='experiments.Experiment',
        verbose_name=_('experiment'),
    )
    question = models.ForeignKey(
        on_delete=models.PROTECT,
        to='stages.Question',
        verbose_name=_('question'),
    )
    value = models.TextField(
        verbose_name=_('value'),
    )

    class Meta:
        unique_together = (
            'experiment',
            'question',
        )
        verbose_name = _('question answer')
        verbose_name_plural = _('question answers')

    def __str__(self):
        return _(
            'Answer for question "{}" for experiment {}'
        ).format(
            self.question,
            self.experiment
        )
