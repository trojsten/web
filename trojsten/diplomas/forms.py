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

        self.diploma_templates = templates

        template_choices = [(t.pk, t.name) for t in self.diploma_templates]

        self.fields['template'] = forms.ChoiceField(choices=template_choices)

        self.fields['editor'] = forms.CharField(widget=Editor(mode={'name': 'javascript', 'json': True},
                                                              theme='darcula',
                                                              autofocus=True),
                                                required=False)

        self.fields['participants_data'] = forms.CharField(widget=forms.HiddenInput(),
                                                           required=False,
                                                           initial="")

        self.fields['join_pdf'] = forms.BooleanField(initial=True, required=False, label=_('Join pdfs'))

    def clean_participants_data(self):
        data = self.cleaned_data['participants_data']

        result = None

        try:
            result = json.loads(data)
        except json.JSONDecodeError:
            pass

        try:
            f = io.StringIO(data)
            reader = csv.DictReader(f, dialect='excel-tab')
            result = [dict(row) for row in reader]
        except csv.Error:
            pass

        if not result:
            raise forms.ValidationError("Failed to parse the input data")

        return result