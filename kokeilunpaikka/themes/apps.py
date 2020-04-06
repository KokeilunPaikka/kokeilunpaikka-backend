from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ThemesConfig(AppConfig):
    name = 'kokeilunpaikka.themes'
    verbose_name = _('Themes')
