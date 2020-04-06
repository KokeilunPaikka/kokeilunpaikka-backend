from .base import *  # noqa: F401, F403

SITE_ID = 1
ALLOWED_HOSTS = ['www.kokeilunpaikka.fi']

DEBUG = False

DEFAULT_FROM_EMAIL = 'no-reply@kokeilunpaikka.fi'

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'motiva-production'
GS_LOCATION = 'kokeilunpaikka'
GS_FILE_OVERWRITE = False
THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE
