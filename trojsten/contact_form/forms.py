from __future__ import  unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from contact_form import forms as contact_forms


class ContactForm(contact_forms.ContactForm):
    subject = forms.CharField(max_length=100,
                              label=_('Subject'))

    def from_email(self):
        return self.cleaned_data['email']

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)


