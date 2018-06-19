# -*- coding: utf-8 -*-
import os

from django import forms
from django.conf import settings
from django.utils.html import format_html, escape
from django.utils.translation import ugettext_lazy as _

from trojsten.diplomas.models import DiplomaTemplate

from . import constants


class DiplomaParametersForm(forms.Form):

    # def __init__(self, *args, **kwargs):
    #     super(DiplomaParametersForm, self).__init__(*args, **kwargs)
    #     self.fields[]

    diploma_templates = DiplomaTemplate.objects.get_queryset()
    template_choices = [(t.pk, t.name) for t in diploma_templates]

    template = forms.ChoiceField(choices=template_choices)
    join_pdf = forms.BooleanField(initial=True, required=False)
    participant_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH,
        required=False
    )
    participant_json_data = forms.CharField(widget=forms.HiddenInput(), required=False)

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
