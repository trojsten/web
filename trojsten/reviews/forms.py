# -*- coding: utf-8 -*-
import os
import re
import sys
import zipfile
from functools import partial, wraps
from time import time

from django import forms
from django.conf import settings
from django.forms.formsets import BaseFormSet, formset_factory
from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext_lazy as _
from easy_select2 import Select2
from unidecode import unidecode

from trojsten.people.models import User
from trojsten.reviews.constants import RE_FILENAME, RE_LAST_NAME, RE_SUBMIT_PK
from trojsten.reviews.helpers import edit_review, get_latest_submits_for_task, submit_review
from trojsten.submit.constants import SUBMIT_STATUS_IN_QUEUE
from trojsten.submit.helpers import write_chunks_to_file

try:
    from urllib.request import quote, unquote
except:  # noqa: E722 @FIXME
    from urllib import quote, unquote


reviews_upload_pattern = re.compile(
    r"(?P<%s>.*)_(?P<%s>[0-9]+)/(?!source/)(?P<%s>.+\.[^.]+)"
    % (RE_LAST_NAME, RE_SUBMIT_PK, RE_FILENAME)
)


class UploadZipForm(forms.Form):
    file = forms.FileField(max_length=128, label="Zip súbor")

    def clean(self):
        cleaned_data = super(UploadZipForm, self).clean()

        if "file" in cleaned_data:
            filename = cleaned_data["file"].name
            if filename.lower().endswith(".zip"):
                return cleaned_data
            else:
                raise forms.ValidationError(_("File must be a ZIP archive: %s") % filename)
        else:
            return False

    def save(self, req_user, task):
        filecontent = self.cleaned_data["file"]

        path = os.path.join(
            settings.SUBMIT_PATH, "reviews", "%s_%s.zip" % (int(time()), req_user.username)
        )
        path = unidecode(path)
        write_chunks_to_file(path, filecontent.chunks())
        return path


class ReviewForm(forms.Form):
    file = forms.FileField(max_length=128, required=False)
    user = forms.ChoiceField(widget=Select2)
    points = forms.IntegerField(min_value=0, required=True)
    comment = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop("choices")
        max_val = kwargs.pop("max_value")
        comment_widget = kwargs.pop("comment_widget", forms.Textarea)
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields["comment"].widget = comment_widget()

        # setting max_value doesn't work
        self.fields["points"] = forms.IntegerField(min_value=0, max_value=max_val, required=True)
        self.fields["user"].choices = choices

    def clean(self):
        cleaned_data = super(ReviewForm, self).clean()

        if "points" not in cleaned_data or cleaned_data["points"] is None:
            raise forms.ValidationError(_("Points are required"))

        if "user" not in cleaned_data or cleaned_data["user"] is None:
            raise forms.ValidationError(_("User is required"))
        user_id = cleaned_data["user"]
        try:
            cleaned_data["user"] = User.objects.get(pk=user_id)
        except:  # noqa: E722 @FIXME
            raise forms.ValidationError(_("User %s does not exist") % user_id)

        return cleaned_data

    def save(self, submit, create=False):
        """If creating a new submit, point to user's submit.
        if not, point to existing reviewed submit.
        """
        user = self.cleaned_data["user"]

        if self.cleaned_data.get("file"):
            filecontent = self.cleaned_data["file"]
            filename = self.cleaned_data["file"].name
        else:
            filecontent = None
            filename = None
        points = self.cleaned_data["points"]
        comment = self.cleaned_data["comment"]

        if create:
            submit_review(filecontent, filename, submit.task, user, points, comment, submit)
        else:
            edit_review(filecontent, filename, submit, user, points, comment)


def get_zip_form_set(choices, max_value, files, *args, **kwargs):
    """Creates ZipFormSet which has forms with filled-in choices"""

    ZipFormWithChoices = wraps(ZipForm)(
        partial(ZipForm, choices=choices, max_value=max_value, valid_files=files)
    )
    return formset_factory(ZipFormWithChoices, *args, formset=BaseZipSet, **kwargs)


class ZipForm(forms.Form):
    filename = forms.CharField(widget=HiddenInput())
    user = forms.ChoiceField(widget=Select2)
    points = forms.IntegerField(min_value=0, required=False)
    comment = forms.CharField(
        widget=forms.widgets.Textarea(attrs={"rows": 1, "cols": 30}), required=False
    )

    def __init__(self, data=None, *args, **kwargs):
        choices = kwargs.pop("choices")
        max_val = kwargs.pop("max_value")
        self.valid_files = kwargs.pop("valid_files")

        super(ZipForm, self).__init__(data, *args, **kwargs)

        self.fields["user"].choices = choices
        if "initial" in kwargs and "filename" in kwargs["initial"]:
            try:
                kwargs["initial"]["filename"].encode("utf8")
            except:  # noqa: E722 @FIXME
                kwargs["initial"]["filename"] = quote(kwargs["initial"]["filename"])
            self.filename = kwargs["initial"]["filename"]
            self.name = kwargs["initial"]["filename"]

        if "initial" in kwargs and "comment" in kwargs["initial"]:
            try:
                try:
                    kwargs["initial"]["comment"] = kwargs["initial"]["comment"].decode("utf8")
                except:  # noqa: E722 @FIXME
                    kwargs["initial"]["comment"] = kwargs["initial"]["comment"].decode(
                        "windows-1250"
                    )
            except:  # noqa: E722 @FIXME
                kwargs["initial"]["comment"] = unidecode(kwargs["initial"]["comment"])

        self.fields["points"] = forms.IntegerField(min_value=0, required=False, max_value=max_val)

    def clean(self):
        cleaned_data = super(ZipForm, self).clean()
        self.name = cleaned_data["filename"]
        if sys.version_info[0] == 3:
            # FIXME: remove this check when we stop supporting python2.7
            cleaned_data["filename"] = unquote(cleaned_data["filename"])
        else:
            try:
                cleaned_data["filename"] = unquote(cleaned_data["filename"].encode("ascii"))
            except:  # noqa: E722 @FIXME
                pass

        if cleaned_data["user"] == "None":
            cleaned_data["user"] = None
        else:
            cleaned_data["user"] = User.objects.get(pk=cleaned_data["user"])

        if cleaned_data["user"] is None:
            return cleaned_data

        if cleaned_data["filename"] not in self.valid_files:
            raise forms.ValidationError(_("Invalid filename %s") % cleaned_data["filename"])

        if cleaned_data["points"] is None:
            raise forms.ValidationError(_("Must have set points"))

        return cleaned_data


class BaseZipSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        users = set()
        for form in self.forms:
            user = form.cleaned_data["user"]
            if user is None:
                continue

            if user and user in users:
                raise forms.ValidationError(_("Assigned 2 or more files to the same user."))

            users.add(user)

    def save(self, archive_path, task):
        with zipfile.ZipFile(archive_path) as archive:
            for form in self:
                user = form.cleaned_data["user"]

                if user is None:
                    continue

                fname = form.cleaned_data["filename"]
                points = form.cleaned_data["points"]
                comment = form.cleaned_data["comment"]

                submit_review(
                    archive.read(fname), os.path.basename(fname), task, user, points, comment
                )

        os.remove(archive_path)


class BasePointForm(forms.Form):
    def __init__(self, max_points, *args, **kwargs):
        self.max_points = max_points
        super(BasePointForm, self).__init__(*args, **kwargs)
        self.fields["user"] = forms.ModelChoiceField(queryset=User.objects.all())
        self.fields["points"] = forms.DecimalField(
            max_digits=5,
            decimal_places=2,
            required=False,
            min_value=0,
            max_value=self.max_points,
            widget=forms.TextInput(attrs={"tabindex": "1"}),
        )
        self.fields["reviewer_comment"] = forms.CharField(
            required=False, widget=forms.Textarea(attrs={"rows": 1, "tabindex": 1})
        )


class BasePointFormSet(forms.BaseFormSet):
    def save(self, task):
        users = get_latest_submits_for_task(task)
        for form_data in self.cleaned_data:
            user = form_data["user"]
            if user in users:
                value = users[user]
                if form_data["points"] is not None:
                    if "review" in value:
                        edit_review(
                            None,
                            None,
                            value["review"],
                            user,
                            form_data["points"],
                            form_data["reviewer_comment"],
                        )
                    else:
                        submit_review(
                            None,
                            None,
                            task,
                            user,
                            form_data["points"],
                            form_data["reviewer_comment"],
                            value["description"],
                        )
                else:
                    if "review" in value:
                        submit = value["review"]
                        submit.points = 0
                        submit.testing_status = SUBMIT_STATUS_IN_QUEUE
                        submit.save()
