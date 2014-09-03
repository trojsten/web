# coding: utf-8
from __future__ import unicode_literals
from django import forms
from django.conf import settings


class SourceSubmitForm(forms.Form):
    LANGUAGE_CHOICES = (
        (".", "Zisti podľa prípony"),
        (".cc", "C++ (.cpp/.cc)"),
        (".pas", "Pascal (.pas/.dpr)"),
        (".c", "C (.c)"),
        (".py", "Python 3.2 (.py/.py3)"),
        (".hs", "Haskell (.hs)"),
        (".cs", "C# (.cs)"),
        (".java", "Java (.java)")
    )
    submit_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH)
    language = forms.ChoiceField(label='Jazyk',
                                 choices=LANGUAGE_CHOICES)


class DescriptionSubmitForm(forms.Form):
    submit_file = forms.FileField(
        max_length=settings.UPLOADED_FILENAME_MAXLENGTH)
