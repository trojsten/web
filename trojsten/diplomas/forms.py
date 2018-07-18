# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import csv
import json

from django import forms
from django.utils.translation import ugettext_lazy as _

from .widgets import Editor


class DiplomaParametersForm(forms.Form):

    def __init__(self, templates, *args, **kwargs):
        super(DiplomaParametersForm, self).__init__(*args, **kwargs)

        template_choices = [(t.pk, t.name) for t in templates]

        self.fields['template'] = forms.ChoiceField(choices=template_choices, label=_('Template'))

        self.fields['editor'] = forms.CharField(widget=Editor(mode={'name': 'javascript', 'json': True},
                                                              autofocus=True),
                                                required=False,
                                                disabled=True)

        self.fields['participants_data'] = forms.CharField(widget=forms.HiddenInput(),
                                                           required=False,
                                                           initial="")

        self.fields['join_pdf'] = forms.BooleanField(initial=True, required=False, label=_('Join into one PDF'))

    def clean_participants_data(self):
        data = self.cleaned_data['participants_data']

        result = None
        try:
            result = json.loads(data)
        except json.JSONDecodeError:
            pass
        if result:
            return result

        try:
            f = io.StringIO(data)
            reader = csv.DictReader(f, dialect='excel-tab')
            result = [dict(row) for row in reader]
        except csv.Error:
            pass
        if result:
            return result

        raise forms.ValidationError(_("Failed to parse the input data"))
