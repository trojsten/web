# -*- coding: utf-8 -*-
import os
import json

from django import forms
from django.conf import settings
from django.utils.html import format_html, escape
from django.utils.translation import ugettext_lazy as _

from .helpers import parse_participants


class DiplomaParametersForm(forms.Form):

    def __init__(self, templates, *args, **kwargs):
        self.diploma_templates = templates

        super(DiplomaParametersForm, self).__init__(*args, **kwargs)

        template_choices = [(t.pk, t.name) for t in self.diploma_templates]

        self.fields['template'] = forms.ChoiceField(choices=template_choices)
        self.fields['join_pdf'] = forms.BooleanField(initial=True, required=False)
        self.fields['participants_data'] = forms.FileField(
            max_length=settings.UPLOADED_FILENAME_MAXLENGTH,
            required=False
        )
        self.fields['single_participant_data'] = forms.CharField(widget=forms.HiddenInput(),
                                                                 required=False,
                                                                 initial="[{}]")

    def clean_participants_data(self):
        pfile = self.cleaned_data['participants_data']
        if pfile is None:
            return pfile
        extension = os.path.splitext(pfile.name)[1]
        if extension.lower() not in settings.DIPLOMA_PARTICIPANTS_ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                format_html(
                    _("Uploaded file with unsupported extension {extension}<br/>"
                      "Supported extensions are {allowed}"),
                    extension=escape(extension),
                    allowed=escape(" ".join(settings.DIPLOMA_PARTICIPANTS_ALLOWED_EXTENSIONS))
                )
            )
        participants_data, error_msg = parse_participants(pfile)
        if error_msg != "":
            raise forms.ValidationError("Failed to parse the supplied file")
        return participants_data

    def clean_single_participant_data(self):
        data = self.cleaned_data['single_participant_data']
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise forms.ValidationError("Supplied data invalid")

    def clean(self):
        super(DiplomaParametersForm, self).clean()
        file_data = self.cleaned_data['participants_data']
        if file_data is not None:
            self.cleaned_data['participants_data'] = file_data
            return self.cleaned_data

        is_json_empty = True
        json_data = self.cleaned_data['single_participant_data']
        for k, v in json_data[0].items():
            if v != "":
                is_json_empty = False
                break

        if is_json_empty:
            raise forms.ValidationError("You have to either upload a file or fill the fields")

        self.cleaned_data['participants_data'] = json_data
        return self.cleaned_data
