from __future__ import unicode_literals

from contact_form import forms as contact_forms
from django import forms
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import ugettext_lazy as _
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget


class ContactForm(contact_forms.ContactForm):
    subject = forms.CharField(max_length=160,
                              required=True,
                              label=_('Subject'))

    field_order = ['name', 'email', 'subject', 'body']

    def __init__(self, captcha, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.to = settings.CONTACT_FORM_RECIPIENTS
        self.fields['name'].label = _('Name')
        self.fields['email'].label = _('Email')
        self.fields['body'].label = _('Message')
        if captcha:
            self.fields['captcha'] = ReCaptchaField(widget=ReCaptchaWidget())

    def body(self):
        return self.message()

    def reply_to(self):
        return [
            '{name}<{email}>'.format(
                name=self.cleaned_data['name'], email=self.cleaned_data['email']
            )
        ]

    def get_message_dict(self):
        """
        Generate the various parts of the message and return them in a
        dictionary, suitable for passing directly as keyword arguments
        to ``django.core.mail.EmailMessage()``.

        By default, the following values are returned:

        * ``from_email``

        * ``body``

        * ``to``

        * ``subject``

        """
        if not self.is_valid():
            raise ValueError(
                "Message cannot be sent from invalid contact form"
            )
        message_dict = {}
        for message_part in ('from_email', 'body',
                             'to', 'subject', 'reply_to'):
            attr = getattr(self, message_part)
            message_dict[message_part] = attr() if callable(attr) else attr
        return message_dict

    def save(self, fail_silently=False):
        EmailMessage(**self.get_message_dict()).send(fail_silently=fail_silently)
