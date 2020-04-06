from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..utils.models import TimeStampedModel


class Image(TimeStampedModel):
    """Model to store information about an image upload.

    This way every uploaded image gets a unique id which can then be referred
    to in any API requests which need to attach image information for
    resources.
    """
    image = models.ImageField(
        verbose_name=_('image'),
    )
    uploaded_by = models.ForeignKey(
        null=True,
        on_delete=models.SET_NULL,
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('uploaded by'),
    )

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
