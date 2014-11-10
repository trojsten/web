from functools import partial, wraps

from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import HiddenInput
from django import forms


class ReviewForm(forms.Form):
    file = forms.FileField(max_length=128)
    user = forms.ChoiceField()
    points = forms.IntegerField(min_value=0, required=False)

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop("choices")
        max_value = kwargs.pop("max_value")
        super(ReviewForm, self).__init__(*args, **kwargs)

        self.fields["user"].choices = choices
        self.fields["points"].max_value = max_value


def get_zip_form_set(choices, max_value, *args, **kwargs):
    """Creates ZipFormSet which has forms with filled-in choices"""

    ZipFormWithChoices = wraps(ZipForm)(partial(ZipForm, choices=choices, max_value=max_value))
    return formset_factory(ZipFormWithChoices, *args, formset=BaseZipSet, **kwargs)


class ZipForm(forms.Form):
    filename = forms.CharField(widget=HiddenInput())
    user = forms.ChoiceField()
    points = forms.IntegerField(min_value=0, required=False)

    def __init__(self, data=None, *args, **kwargs):
        choices = kwargs.pop("choices")
        max_value = kwargs.pop("max_value")
        super(ZipForm, self).__init__(data, *args, **kwargs)

        self.fields["user"].choices = choices
        if 'initial' in kwargs: 
            self.name = kwargs["initial"]["filename"]

        self.fields["points"].max_value = max_value

    def clean(self):
        cleaned_data = super(ZipForm, self).clean()

        if cleaned_data["points"] is None and cleaned_data["user"] != "None":
            raise forms.ValidationError(_("Must have set points, or user must be empty"))

        return cleaned_data

class BaseZipSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        users = set()
        for form in self.forms:
            user = form.cleaned_data['user']
            if user and user in users:
                raise forms.ValidationError(_("Assigned 2 or more files to the same user."))
            
            users.add(user)
