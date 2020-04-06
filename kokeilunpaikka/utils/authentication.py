from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ExpiringTokenAuthentication(TokenAuthentication):
    """Extend TokenAuthentication to require login after expiration time."""

    INVALID_TOKEN = 'invalid_token'
    TOKEN_EXPIRED = 'token_expired'

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise AuthenticationFailed(
                detail=_('Invalid token.'),
                code=self.INVALID_TOKEN
            )

        if not token.user.is_active:
            raise AuthenticationFailed(
                detail=_('User inactive or deleted.'),
                code=self.INVALID_TOKEN
            )

        if token.created < timezone.now() - timedelta(
            hours=settings.REST_TOKEN_EXPIRATION_TIME
        ):
            raise AuthenticationFailed(
                detail=_('Token has expired.'),
                code=self.TOKEN_EXPIRED
            )

        return (token.user, token)


def create_expiring_token(token_model, user, serializer):
    token, created = token_model.objects.get_or_create(user=user)

    if not created:
        # Update the created time of the token to keep it valid
        token.created = timezone.now()
        token.save()

    return token
