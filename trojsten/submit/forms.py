# coding: utf-8
from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy

import os


class SourceSubmitForm(forms.Form):
    LANGUAGE_CHOICES = (
        # Translators: original: Zisti podľa prípony
        (".", ugettext_lazy('Find out by extension')),
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
    # Translators: original: Jazyk
    language = forms.ChoiceField(label=ugettext_lazy('Language'),
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
            # Translators: original: Zaslaný súbor má nepodporovanú príponu %s
            raise forms.ValidationError(ugettext_lazy("The submitted file has unsupported extension %s") % extension)
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
                # Translators: original: Zaslaný súbor nemá koncovku .zip
                raise forms.ValidationError(ugettext_lazy("The submitted file does not have the extension .zip"))
        else:
            # Translators: original: Chýba súbor
            raise forms.ValidationError(ugettext_lazy("File is missing"))
