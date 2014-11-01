# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms


class RegistrationForm(forms.Form):
    PROP_FIELD_NAME = 'prop_%d'

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
            except:
                initial = None
            self.fields[RegistrationForm.PROP_FIELD_NAME % prop.id] = forms.CharField(
                label=prop.key_name, required=False, initial=initial
            )
