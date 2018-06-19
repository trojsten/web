# -*- coding: utf-8 -*-
import os
import json

from django import forms
from django.conf import settings
from django.utils.html import format_html, escape
from django.utils.translation import ugettext_lazy as _

from trojsten.diplomas.models import DiplomaTemplate


class DiplomaParametersForm(forms.Form):

    def __init__(self, templates, *args, **kwargs):
        self.diploma_templates = templates

        super(DiplomaParametersForm, self).__init__(*args, **kwargs)

        template_choices = [(t.pk, t.name) for t in self.diploma_templates]

        self.fields['template'] = forms.ChoiceField(choices=template_choices)
        self.fields['join_pdf'] = forms.BooleanField(initial=True, required=False)
        self.fields['participant_file'] = forms.FileField(
            max_length=settings.UPLOADED_FILENAME_MAXLENGTH,
            required=False
        )
        self.fields['participant_json_data'] = forms.CharField(widget=forms.HiddenInput(),
                                                               required=False,
                                                               initial="{}")

    def clean_participant_file(self):
        pfile = self.cleaned_data['participant_file']
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
        return pfile

    def clean_participant_json_data(self):
        data = self.cleaned_data['participant_json_data']
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise forms.ValidationError("Supplied data invalid")
