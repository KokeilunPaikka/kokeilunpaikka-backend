from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ExperimentsConfig(AppConfig):
    name = 'kokeilunpaikka.experiments'
    verbose_name = _('Experiments')
