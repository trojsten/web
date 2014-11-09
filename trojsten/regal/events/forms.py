# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList

from ..people.models import UserProperty


class RegistrationForm(forms.Form):
    PROPERTY_FIELD_PREFIX = 'prop_'
    PROPERTY_FIELD_NAME_TEMPLATE = PROPERTY_FIELD_PREFIX + '%d'

    # values are represented as strings ('True', 'False') on client side
    # coerce is used to convert this values to bool
    going = forms.TypedChoiceField(
        label='Prihlasujem sa ako %s',
        coerce=lambda x: x == 'True',
        choices=((True, 'Áno'), (False, 'Nie')),
        widget=forms.RadioSelect,
    )

    def __init__(self, invite, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.invite = invite
        self.fields['going'].label %= self.invite.get_type_display()
        for prop in self.invite.event.registration.required_user_properties.all():
            try:
                initial = invite.user.properties.get(key=prop).value
            except UserProperty.DoesNotExist:
                initial = None
            self.fields[self.PROPERTY_FIELD_NAME_TEMPLATE % prop.id] = forms.CharField(
                label=prop.key_name, required=False, initial=initial
            )

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        for field_name in self.fields:
            if field_name.startswith(RegistrationForm.PROPERTY_FIELD_PREFIX):
                if cleaned_data.get('going', False) and not cleaned_data[field_name]:
                    if field_name not in self._errors:
                        self._errors[field_name] = ErrorList()
                    self._errors[field_name].append(_('This field is required.'))
        return cleaned_data
