from __future__ import absolute_import, unicode_literals

import logging
import types

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils import translation

logger = logging.getLogger(__name__)


def send_template_mail(recipient, template, variables,
                       sender=None, html=True, subject=None, lang=None):
    """
    Send an e-mail using a template.

    Arguments:
    recipient -- the address(es) of the recipient(s)
    template  -- the template name to use. See below for details.
    variables -- a dictionary of variables to use in the template context.
    sender    -- the sender address. If not specified, a built-in default
                 will be used.
    html      -- if set to False, no HTML part will be used even if available.
    subject   -- if not None, this will be used as the message subject instead
                 of the subject template.
    lang      -- if not None, this will be used as the language of the
                 template.

    In case of failure, a log entry is printed and False returned.

    Template name:

    The template will be searched from the "email" subdirectory of the template
    root. The extensions ".html" and ".txt" will be tried. The
    ".txt" template must be present. The HTML template, if present, will
    be used as the message's alternative content.

    A template named "(template name).subject" will be used as the message
    subject.

    If a template with a language extension matching the current language
    exists (e.g. "mytemplate_fi.txt"), it will be used.

    Context:

    The dictionary given as argument will be made available to the templates.
    In addition, the following keys will also be available (unless overriden
    by the user passed dictionary.)

    recipient   -- the address of the recipient
    sender      -- the address of the sender
    """

    if isinstance(recipient, str):
        recipient = (recipient,)
    elif isinstance(recipient, types.GeneratorType):
        recipient = tuple(recipient)

    if not recipient:
        logger.info("Not sending template mail (%s) to any \recipient from %s",
                    template, sender)
        return False

    sender = sender or getattr(settings, 'DEFAULT_FROM_EMAIL')

    lang = lang if lang is not None else translation.get_language()

    logger.info("Sending template mail (%s) from %s in language %s",
                template, sender, lang)

    ctx = {
        'recipient': recipient,
        'sender': sender,
    }
    ctx.update(variables)

    if subject is None:
        subject = _get_localized_template(template, lang, "subject").render(ctx).strip()
    plaintext = _get_localized_template(template, lang, "txt").render(ctx)

    alttext = None
    if html:
        try:
            alttext = _get_localized_template(template, lang, "html").render(ctx)
        except TemplateDoesNotExist:
            # HTML part is optional
            pass

    msg = EmailMultiAlternatives(subject, plaintext, sender, recipient)
    if alttext:
        msg.attach_alternative(alttext, "text/html")

    return msg.send()


def _get_localized_template(name, language, suffix):
    """
    Internal: Get the best version of the template for the given language.
    The search order is:
    template_XX-XX.suffix
    template_XX.suffix
    template.suffix
    """
    try:
        if language:
            return get_template("email/{}_{}.{}".format(name, language, suffix))
        else:
            return get_template("email/{}.{}".format(name, suffix))

    except TemplateDoesNotExist:
        if not language:
            raise
        elif '-' in language:
            return _get_localized_template(name, language.split('-')[0], suffix)
        else:
            return _get_localized_template(name, '', suffix)
