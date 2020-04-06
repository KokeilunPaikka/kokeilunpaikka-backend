from django.contrib.auth.apps import AuthConfig


class AuthenticationConfig(AuthConfig):
    name = 'extensions.auth'
    label = 'authentication'
