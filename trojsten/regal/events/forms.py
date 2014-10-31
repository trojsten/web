# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms


class RegistrationForm(forms.Form):
    going = forms.TypedChoiceField(
        label='Prídem',
        coerce=lambda x: x == 'True',
        choices=((True, 'Áno'), (False, 'Nie')),
        widget=forms.RadioSelect,
    )

    def __init__(self, event, *args, **kwargs):
        self.event = event
        super(RegistrationForm, self).__init__(*args, **kwargs)
