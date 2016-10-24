# coding: utf-8
from __future__ import unicode_literals

import os

from django import forms
from django.conf import settings
from django.utils.html import format_html, escape

class SourceSubmitForm(forms.Form):
    LANGUAGE_CHOICES = (
        (".", "Zisti podľa prípony"),
        (".cc", "C++ (.cpp/.cc)"),
        (".pas", "Pascal (.pas/.dpr)"),
        (".c", "C (.c)"),
        (".py", "Python 3.4 (.py/.py3)"),
        (".hs", "Haskell (.hs)"),
        (".cs", "C# (.cs)"),
        (".java", "Java (.java)")
    )
    submit_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH,
        allow_empty_file=True,
    )
    language = forms.ChoiceField(label='Jazyk',
                                 choices=LANGUAGE_CHOICES)


class DescriptionSubmitForm(forms.Form):
    submit_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH,
        allow_empty_file=True,
    )

    def clean_submit_file(self):
        sfile = self.cleaned_data['submit_file']
        extension = os.path.splitext(sfile.name)[1]
        if extension.lower() not in settings.SUBMIT_DESCRIPTION_ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                format_html(
                    "Zaslaný súbor má nepodporovanú príponu {extension}<br />"
                    "Podporované prípony sú {allowed}",
                    extension=escape(extension),
                    allowed=escape(" ".join(settings.SUBMIT_DESCRIPTION_ALLOWED_EXTENSIONS))
                )
            )
        return sfile


class TestableZipSubmitForm(forms.Form):
    submit_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH,
        allow_empty_file=True,
    )

    def clean_submit_file(self):
        sfile = self.cleaned_data['submit_file']
        if sfile:
            if sfile.name.split('.')[-1].lower() != 'zip':
                raise forms.ValidationError("Zaslaný súbor nemá koncovku .zip")
        else:
            raise forms.ValidationError("Chýba súbor")
