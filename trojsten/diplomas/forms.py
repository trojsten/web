# -*- coding: utf-8 -*-

import io
import csv
import json
import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from .widgets import Editor


class DiplomaParametersForm(forms.Form):

    def __init__(self, templates, *args, **kwargs):
        super(DiplomaParametersForm, self).__init__(*args, **kwargs)

        self.fields['template'] = forms.ChoiceField(choices=[(t.pk, t.name) for t in templates], label=_('Template'))

        self.fields['editor'] = forms.CharField(
            widget=Editor(mode={'name': 'javascript', 'json': True},
                          autofocus=True),
            required=False,
            disabled=True,
            initial=kwargs.get('data', {}).get('participants_data', ''))

        self.fields['participants_data'] = forms.CharField(widget=forms.HiddenInput(),
                                                           required=False,
                                                           initial="",
                                                           label=_('Participants data'))

        self.fields['join_pdf'] = forms.BooleanField(initial=True, required=False, label=_('Join into one PDF'))

    def clean_participants_data(self):
        data = self.cleaned_data['participants_data']
        data = re.sub(r'[\t]+', '\t', data)

        result = None
        try:
            result = json.loads(data)
        except json.JSONDecodeError:
            pass
        if result:
            return result

        try:
            f = io.StringIO(data)
            reader = csv.DictReader(f, dialect='excel-tab', strict=True)
            result = [dict(row) for row in reader]
            for row in result:
                for k in row.keys():
                    if not k.isalnum():      # Otherwise the reader would parse just about anything...
                        result = None
                        raise csv.Error
        except csv.Error:
            pass
        if result:
            return result

        raise forms.ValidationError(_("Failed to parse the input data"))
