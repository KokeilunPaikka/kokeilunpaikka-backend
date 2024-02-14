"""
Django settings for sofokus_django_base project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import logging
import os

from django.utils.translation import ugettext_lazy as _

from corsheaders.defaults import default_headers

logger = logging.getLogger(__name__)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# Declare explicitly to quiet Django >3.2 warnings
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # This must be placed before rest_framework
    'kokeilunpaikka.docs.apps.ConfigAppConfig',

    # Dependencies
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'easy_thumbnails',
    'rest_auth',
    'parler',
    'ckeditor',
    'django_filters',

    # Custom apps
    'extensions.auth.apps.AuthenticationConfig',
    'kokeilunpaikka.experiments.apps.ExperimentsConfig',
    'kokeilunpaikka.library.apps.LibraryConfig',
    'kokeilunpaikka.uploads.apps.UploadsConfig',
    'kokeilunpaikka.themes.apps.ThemesConfig',
    'kokeilunpaikka.users.apps.UsersConfig',
    'kokeilunpaikka.stages.apps.StagesConfig',
    'kokeilunpaikka.sitemap.apps.SitemapConfig',
    'importer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Custom user model
# https://docs.djangoproject.com/en/2.1/topics/auth/customizing/#substituting-a-custom-user-model
AUTH_USER_MODEL = 'authentication.User'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# LOCALIZATION AND LANGUAGE
############################

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'fi'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True
USE_THOUSAND_SEPARATOR = True

USE_TZ = True

LANGUAGES = (
    ('fi', _('fin')),
    ('sv', _('sve')),
    ('en', _('eng')),
)

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)

PARLER_LANGUAGES = {
    1: (
        {'code': 'fi'},
        {'code': 'sv'},
        {'code': 'en'},
    ),
    'default': {
        'fallbacks': ['fi', 'sv', 'en'],
    }
}

# STATIC FILES AND MEDIA URLS
##############################

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/backend_static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'files', 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'files', 'static')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# DATABASE
##########
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT', ''),
    }
}

# SECURITY
##########

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# LOGGING
##########
LOG_ROOT = BASE_DIR + '/log/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'WARNING',
        'handlers': ['logfile'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },

    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'simple',
            'filename': LOG_ROOT + 'application.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# DJANGO REST FRAMEWORK
##########
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'kokeilunpaikka.utils.authentication.ExpiringTokenAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'EXCEPTION_HANDLER': 'kokeilunpaikka.utils.exceptions.custom_exception_handler',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'kokeilunpaikka.users.serializers.UserDetailsSerializer',
}

REST_TOKEN_EXPIRATION_TIME = 24 * 7  # hours

REST_AUTH_TOKEN_CREATOR = 'kokeilunpaikka.utils.authentication.create_expiring_token'

BASE_FRONTEND_URL = os.environ.get('BASE_FRONTEND_URL')

PASSWORD_RESET_URL = os.environ.get('PASSWORD_RESET_URL', '/reset/{uid}/{token}/')

# CORS HEADERS
##########
CORS_ORIGIN_WHITELIST = os.environ.get('CORS_ORIGIN_HOSTNAME', '').split(',')

CORS_ALLOW_HEADERS = list(default_headers) + [
    'content-disposition',
]

# THUMBNAIL SETTINGS (for easy-thumbnails)
##########
THUMBNAIL_ALIASES = {
    '': {
        'square_detail_image': {'size': (606, 606), 'crop': True, 'quality': 80},
        'small_profile_image': {'size': (120, 120), 'crop': True, 'quality': 80},
        'list_image': {'size': (720, 480), 'crop': True, 'quality': 80},
        'post_image': {'size': (944, 580), 'crop': True, 'quality': 80},
        'hero_image': {'size': (1280, 460), 'crop': True, 'quality': 80},
    },
}

# CKEDITOR WIDGET
##########
CKEDITOR_CONFIGS = {
    'default': {
        'height': 400,
        'width': 900,
        'autoGrow_minHeight': 400,
        'autoGrow_maxHeight': 1000,
        'autoGrow_onStartup': True,
        'entities': False,
        'toolbar': 'custom',
        'toolbar_custom': [
            ['Undo', 'Redo'],
            ['Format'],
            ['Bold', 'Italic', 'Underline', 'Strike'],
            ['TextColor', 'BGColor'],
            ['PasteText', 'PasteFromWord'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
            ['Link', 'Unlink'],
            ['NumberedList', 'BulletedList'],
            ['Source'],
        ],
        'extraPlugins': ','.join([
            'autogrow',
        ]),
        'removePlugins': 'stylesheetparser',
        'allowedContent': True,
    },
}
