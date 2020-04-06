from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StagesConfig(AppConfig):
    name = 'kokeilunpaikka.stages'
    verbose_name = _('Stages')
