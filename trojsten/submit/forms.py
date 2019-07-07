# coding: utf-8
from __future__ import unicode_literals

import os

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import escape, format_html
from django.utils.translation import ugettext_lazy as _

from trojsten.submit import constants
from trojsten.submit.helpers import get_description_file_path, write_chunks_to_file
from trojsten.submit.models import Submit


class SourceSubmitForm(forms.Form):
    LANGUAGE_CHOICES = (
        (".", "Zisti podľa prípony"),
        (".cc", "C++ (.cpp/.cc)"),
        (".pas", "Pascal (.pas/.dpr)"),
        (".c", "C (.c)"),
        (".py", "Python 3.4 (.py/.py3)"),
        (".hs", "Haskell (.hs)"),
        (".cs", "C# (.cs)"),
        (".java", "Java (.java)"),
    )
    submit_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH, allow_empty_file=True
    )
    language = forms.ChoiceField(label="Jazyk", choices=LANGUAGE_CHOICES)


class DescriptionSubmitForm(forms.Form):
    submit_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH, allow_empty_file=True
    )

    def clean_submit_file(self):
        sfile = self.cleaned_data["submit_file"]
        extension = os.path.splitext(sfile.name)[1]
        if extension.lower() not in settings.SUBMIT_DESCRIPTION_ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                format_html(
                    "Zaslaný súbor má nepodporovanú príponu {extension}<br />"
                    "Podporované prípony sú {allowed}",
                    extension=escape(extension),
                    allowed=escape(" ".join(settings.SUBMIT_DESCRIPTION_ALLOWED_EXTENSIONS)),
                )
            )
        return sfile


class TestableZipSubmitForm(forms.Form):
    submit_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH, allow_empty_file=True
    )

    def clean_submit_file(self):
        sfile = self.cleaned_data["submit_file"]
        if sfile:
            if sfile.name.split(".")[-1].lower() != "zip":
                raise forms.ValidationError("Zaslaný súbor nemá koncovku .zip")
        else:
            raise forms.ValidationError("Chýba súbor")


class SubmitAdminForm(forms.ModelForm):
    submit_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH,
        allow_empty_file=True,
        label=_("Submit file"),
        help_text=_("Here you can upload a file with submit description"),
        required=False,
    )

    def clean(self):
        cleaned_data = super(SubmitAdminForm, self).clean()
        if (
            cleaned_data["submit_file"]
            and cleaned_data["submit_type"] != constants.SUBMIT_TYPE_DESCRIPTION
        ):
            raise ValidationError(
                _("You can attach a submit file only to descriptions."), code="invalid"
            )
        return cleaned_data

    def save(self, commit=True):
        submit = super(SubmitAdminForm, self).save(commit)
        file = self.cleaned_data.get("submit_file")
        if file:
            user = self.cleaned_data.get("user")
            task = self.cleaned_data.get("task")

            sfiletarget = get_description_file_path(file, user, task)
            write_chunks_to_file(sfiletarget, file.chunks())
            submit.filepath = sfiletarget
        if commit:
            submit.save()
        return submit

    class Meta:
        model = Submit
        fields = "__all__"
