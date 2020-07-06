import os
import logging

from time import sleep
from threading import Thread
from extensions.mailer.mailer import send_template_mail
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


class ExperimentEmailThread(Thread):
    def __init__(self, recipients, experiment_slug, user_name):
        self.recipients = recipients
        self.experiment_slug = experiment_slug
        self.user_name = user_name
        Thread.__init__(self)

    def run(self):
        for r in self.recipients:
            mail_sent = send_template_mail(
                recipient=r,
                subject=_('New experiment that you might be interested in'),
                template='new_experiment_notification',
                variables={
                    "user": self.user_name,
                    "profile_url": f'{os.environ.get("BASE_FRONTEND_URL")}?login-to-profile=true',
                    "experiment_url":
                        f'{os.environ.get("BASE_FRONTEND_URL")}/kokeilu/'
                        + self.experiment_slug
                }
            )
            sleep(0.2)
            if not mail_sent:
                logger.error(
                    'Could not send responsible user add notification email for user '
                    'email %s.',
                    r
                )
