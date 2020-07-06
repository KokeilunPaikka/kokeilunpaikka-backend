from parler.models import TranslatableModel, TranslatedFieldsModel
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..utils.models import TimeStampedModel


class EditableText(TimeStampedModel, TranslatableModel):
    """
    A model that is used to control text content in the
    front end.
    """
    TEXT_TYPES = [
        ('front_page_header', _('Front page header')),
        ('front_page_ingress', _('Front page ingress')),
        ('stages-header', _('Stages header')),
        ('stage-1-header', _('Stage 1 header')),
        ('stage-2-header', _('Stage 2 header')),
        ('stage-3-header', _('Stage 3 header')),
        ('stage-1-text', _('Stage 1 text')),
        ('stage-2-text', _('Stage 2 text')),
        ('stage-3-text', _('Stage 3 text')),
        ('what-are-you-waiting', _('What are you waiting for text')),
        ('footer-paragraph', _('Footer paragraph')),
        ('experiment-browsing', _('Experiment browsing')),
        ('experiment-search-header', _('Experiment search header'))
    ]
    text_type = models.CharField(
        verbose_name=_('text type'),
        max_length=100, choices=TEXT_TYPES,
        unique=True
    )

    def __str__(self):
        return self.get_text_type_display()


class EditableTextTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(
        EditableText,
        related_name='translations',
        null=True,
        on_delete=models.CASCADE
    )
    text_value = models.TextField(verbose_name=_('text value'))

    class Meta:
        unique_together = ('language_code', 'master')


class SiteConfiguration(models.Model):
    active = models.BooleanField(default=False, verbose_name=_('active'))
    front_page_image = models.ImageField(
        verbose_name=_('front page image'),
    )
    front_page_image_opacity = models.FloatField(
        verbose_name=_('front page image opacity'),
        default=0.1
    )
    top_menu_opacity = models.FloatField(
        verbose_name=_('top menu opacity'),
        default=0.25
    )
    featured_experiments = models.ManyToManyField(
        blank=True,
        to='experiments.Experiment',
        verbose_name=_('featured experiments'),
    )
    funded_experiments_amount = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('funded experiments amount')
    )
