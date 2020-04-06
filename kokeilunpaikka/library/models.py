from django.db import models
from django.utils.translation import gettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields

from ..experiments.models import Experiment
from ..utils.models import SanitizedRichTextField, TimeStampedModel
from .querysets import LibraryItemQuerySet


class LibraryItem(TimeStampedModel, TranslatableModel):
    image = models.ImageField(
        upload_to='library_items/',
        verbose_name=_('image'),
    )
    is_visible = models.BooleanField(
        default=True,
        verbose_name=_('is visible'),
    )
    lead_text = models.TextField(
        blank=True,
        verbose_name=_('lead text'),
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

    objects = LibraryItemQuerySet.as_manager()

    class Meta:
        verbose_name = _('library item')
        verbose_name_plural = _('library items')

    def __str__(self):
        return self.name

    @property
    def experiments(self):
        return (
            Experiment.objects
            .active()
            .filter(themes__in=self.themes.values_list('id', flat=True))
            .order_by(
                '-published_at',
                '-created_at'
            )
        )
