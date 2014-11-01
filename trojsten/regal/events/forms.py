# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms


class RegistrationForm(forms.Form):
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
