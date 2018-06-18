# -*- coding: utf-8 -*-
import os

from django import forms
from django.conf import settings
from django.utils.html import format_html, escape
from django.utils.translation import ugettext_lazy as _

from . import constants


class DiplomaParametersForm(forms.Form):
    TEMPLATE_CHOICES = constants.SVG_TEMPLATES
    template = forms.ChoiceField(choices=TEMPLATE_CHOICES)
    join_pdf = forms.BooleanField(initial=True, required=False)
    participant_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH,
        required=False
    )

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
