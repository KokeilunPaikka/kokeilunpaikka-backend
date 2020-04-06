from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields

from ..utils.models import TimeStampedModel


class Theme(TimeStampedModel, TranslatableModel):
    """Theme is a tag-like piece of information that can be attached to any
    Model which should have association with themes.

    Term `theme` is used instead of `tag` to better match the terminology used
    publicly on the site.
    """
    created_by = models.ForeignKey(
        null=True,
        on_delete=models.SET_NULL,
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('created by'),
    )
    is_curated = models.BooleanField(
        default=False,
        help_text=_(
            'User created themes are marked not curated by default.'
        ),
        verbose_name=_('is curated'),
    )

    translations = TranslatedFields(
        name=models.CharField(
            max_length=255,
            verbose_name=_('name'),
        )
    )

    class Meta:
        verbose_name = _('theme')
        verbose_name_plural = _('themes')

    def __str__(self):
        return self.name
