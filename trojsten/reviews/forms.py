from django.forms.formsets import formset_factory
from functools import partial, wraps

from django import forms
from django.forms.widgets import HiddenInput

class ReviewForm (forms.Form):
    file = forms.FileField(max_length=128)
    user = forms.ChoiceField ()
    points = forms.IntegerField(min_value=0, required=False)

    def __init__ (self, *args, **kwargs):
        choices = kwargs.pop("choices")
        max_value = kwargs.pop("max_value")
        super(ReviewForm, self).__init__(*args, **kwargs)

        self.fields["user"].choices = choices
        self.fields["points"] = forms.IntegerField(min_value=0, max_value=max_value, required=False)


def get_zip_form_set (choices, max_value, *args, **kwargs):
    return formset_factory(wraps(ZipForm)(partial(ZipForm, choices=choices, max_value=max_value)), *args, **kwargs)

class ZipForm (forms.Form):
    filename = forms.CharField(widget=HiddenInput())
    user = forms.ChoiceField ()
    points = forms.IntegerField(min_value=0, required=False)

    def __init__ (self, data=None, *args, **kwargs):
        choices = kwargs.pop("choices")
        max_value = kwargs.pop("max_value")
        super(ZipForm, self).__init__(data, *args, **kwargs)

        self.fields["user"].choices = choices
        # self.fields["user"].label = self.fields["filename"].text
        if 'initial' in kwargs: self.name = kwargs["initial"]["filename"]
        self.fields["points"].max_value = max_value