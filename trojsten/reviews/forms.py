import re
from functools import partial, wraps

from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import HiddenInput
from django import forms

from trojsten.regal.tasks.models  import Submit
from trojsten.regal.people.models import User

from trojsten.reviews.helpers import submit_review

reviews_upload_pattern = re.compile(r"(?P<lastname>[^_]*)_(?P<submit_pk>[0-9]+)_(?P<filename>.+\.[^.]+)")

class ReviewForm(forms.Form):
    file = forms.FileField(max_length=128)
    user = forms.ChoiceField()
    points = forms.IntegerField(min_value=0, required=False)

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop("choices")
        max_value = kwargs.pop("max_value")
        super(ReviewForm, self).__init__(*args, **kwargs)

        #setting max_value doesn't work
        self.fields["points"] = forms.IntegerField(min_value=0, max_value=max_value, required=False)
        self.fields["user"].choices = choices


    def clean(self):
        cleaned_data = super(ReviewForm, self).clean()
        
        if "file" not in cleaned_data:
            return {}

        filename = cleaned_data["file"].name
        user = cleaned_data["user"]
        points = cleaned_data["points"]

        if filename.endswith(".zip") and cleaned_data["user"] == "None": 
            cleaned_data["user"] = None
            return cleaned_data

        filematch = reviews_upload_pattern.match(filename)

        if filematch: 
            cleaned_data["file"].name = filematch.group("filename")

        try:
            submit_id = (filematch.group("submit_pk") if filematch else -1)

            if user == "None":
                user = Submit.objects.get(pk=submit_id).user.pk
            cleaned_data["user"] = User.objects.get(pk=user)

        except Submit.DoesNotExist:
            raise forms.ValidationError (_("Auto could not resolve user from filename %s") % filename)

        except (User.DoesNotExist, ValueError):
            raise forms.ValidationError (_("User %s does not exists") % user)

        if points is None:
            raise forms.ValidationError(_("Must have set points"))  

        return cleaned_data

    def save (self, request, task):
        user = self.cleaned_data["user"]
        filecontent = self.cleaned_data["file"].file.read()
        filename = self.cleaned_data["file"].name
        points = self.cleaned_data["points"]

        if user is None and filename.endswith(".zip"):
            path = os.path.join(settings.SUBMIT_PATH, "reviews", "%s_%s.zip" % (int(time()), request.user.pk))
            write_file(filecontent,"", path)
            return path

        submit_review(filecontent, filename, task, user, points)
        return False

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
        if "initial" in kwargs and "filename" in kwargs["initial"]: 
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
