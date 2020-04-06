import logging

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import \
    default_token_generator as token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from extensions.mailer.mailer import send_template_mail

logger = logging.getLogger(__name__)


class User(AbstractUser):

    def password_reset_url(self, uidb64=None, token=None):
        if not uidb64:
            uidb64 = urlsafe_base64_encode(force_bytes(self.pk))
        if not token:
            token = token_generator.make_token(self)

        return settings.BASE_FRONTEND_URL + settings.PASSWORD_RESET_URL.format(
            uid=uidb64,
            token=token,
        )

    def send_registration_notification(self):
        try:
            mail_sent = send_template_mail(
                recipient=self.email,
                subject=_('Thank you for your registration'),
                template='registration_notification',
                variables={
                    'user': self,
                }
            )
        except Exception as e:
            logger.exception(e)
            return

        if not mail_sent:
            logger.error(
                'Could not send registration notification email for user '
                'id %s.',
                self.id
            )
