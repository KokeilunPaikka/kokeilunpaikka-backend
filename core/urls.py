from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from rest_framework.documentation import include_docs_urls

admin.site.site_header = _('kokeilunpaikka.fi administration')
admin.site.site_title = admin.site.site_header


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('api/', include('kokeilunpaikka.experiments.urls')),
    path('api/', include('kokeilunpaikka.library.urls')),
    path('api/', include('kokeilunpaikka.stages.urls')),
    path('api/', include('kokeilunpaikka.themes.urls')),
    path('api/', include('kokeilunpaikka.uploads.urls')),
    path('api/', include('kokeilunpaikka.users.urls')),
    path('api/auth/', include('extensions.auth.rest_auth_urls')),
    path('docs/', include_docs_urls(
        title='Kokeilunpaikka API',
        authentication_classes=[],
        permission_classes=[],
    )),
]

if settings.DEBUG:
    urlpatterns = static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    ) + urlpatterns
