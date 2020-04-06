from django.db import models
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField

from .sanitizer import bleach_clean


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated at'),
    )

    class Meta:
        abstract = True


class SanitizedRichTextField(RichTextField):

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)

        # Clean the HTML from unsafe or unnecessary tags and attributes.
        cleaned_value = bleach_clean(value)

        # "You should also update the model’s attribute if you make any changes
        # to the value so that code holding references to the model will always
        # see the correct value."
        # - https://docs.djangoproject.com/en/2.2/howto/custom-model-fields/#preprocessing-values-before-saving  # noqa
        setattr(model_instance, self.attname, cleaned_value)

        return cleaned_value
