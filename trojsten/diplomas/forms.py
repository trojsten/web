# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from .helpers import parse_csv, parse_json
from .widgets import Editor


class DiplomaParametersForm(forms.Form):
    def __init__(self, templates, *args, **kwargs):
        super(DiplomaParametersForm, self).__init__(*args, **kwargs)

        self.fields["template"] = forms.ChoiceField(
            choices=[(t.pk, t.name) for t in templates], label=_("Template")
        )

        self.fields["editor"] = forms.CharField(
            widget=Editor(mode={"name": "javascript", "json": True}, autofocus=True),
            required=False,
            disabled=True,
            initial=kwargs.get(str("data"), {}).get("participants_data", ""),
        )

        self.fields["participants_data"] = forms.CharField(
            widget=forms.HiddenInput(), required=False, initial="", label=_("Participants data")
        )

        self.fields["join_pdf"] = forms.BooleanField(
            initial=True, required=False, label=_("Join into one PDF")
        )

    def clean_participants_data(self):
        data = self.cleaned_data["participants_data"]
        data = re.sub(r"[\t]+", "\t", data)

        try:
            result = parse_json(data)
        except Exception:
            result = None
        if result:
            return result

        try:
            result = parse_csv(data)
        except Exception:
            result = None
        if result:
            return result

        raise forms.ValidationError(_("Failed to parse the input data"))
