from .base import *  # noqa: F401, F403

SITE_ID = 1
ALLOWED_HOSTS = []

DEBUG = True

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--exe',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
