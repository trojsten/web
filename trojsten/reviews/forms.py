# coding: utf8

from easy_select2 import Select2
import re
import os
from time import time
from functools import partial, wraps
import zipfile

from unidecode import unidecode

from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import HiddenInput
from django import forms
from django.conf import settings

from trojsten.regal.tasks.models import Submit
from trojsten.regal.people.models import User
from trojsten.submit.helpers import write_chunks_to_file

from trojsten.reviews.helpers import submit_review, edit_review

reviews_upload_pattern = re.compile(
    r'(?P<lastname>.*)_(?P<submit_pk>[0-9]+)/(?!source/)(?P<filename>.+\.[^.]+)'
)


class UploadZipForm(forms.Form):
    file = forms.FileField(max_length=128, label='Zip súbor')

    def clean(self):
        cleaned_data = super(UploadZipForm, self).clean()

        filename = cleaned_data['file'].name
        if filename.endswith('.zip'):
            return cleaned_data
        else:
            raise forms.ValidationError(_('Súbor musí byť ZIP archív: %s')
                                        % filename)

    def save(self, req_user, task):
        filecontent = self.cleaned_data['file']
        filename = self.cleaned_data['file'].name

        path = os.path.join(
            settings.SUBMIT_PATH, 'reviews', '%s_%s.zip' % (int(time()), req_user.username)
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
        choices = kwargs.pop('choices')
        max_val = kwargs.pop('max_value')
        comment_widget = kwargs.pop('comment_widget', forms.Textarea)
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget = comment_widget()

        # setting max_value doesn't work
        self.fields['points'] = forms.IntegerField(min_value=0, max_value=max_val, required=True)
        self.fields['user'].choices = choices

    def clean(self):
        cleaned_data = super(ReviewForm, self).clean()
        
        if 'points' not in cleaned_data or cleaned_data['points'] is None:
            raise forms.ValidationError(_('Points are required'))
        points = cleaned_data['points']

        if 'user' not in cleaned_data or cleaned_data['user'] is None:
            raise forms.ValidationError(_('User is required'))
        user_id = cleaned_data['user']
        try:
            cleaned_data['user'] = User.objects.get(pk=user_id)
        except:
            raise forms.ValidationError(_('User %s does not exists') % user_id)

        if 'file' in cleaned_data:
            file = cleaned_data['file']
            filename = cleaned_data['file'].name if file is not None else ''

        return cleaned_data

    def save(self, submit, create=False):
        """if creating a new submit, point to user's submit.
        if not, point to existing reviewed submit."""
        user = self.cleaned_data['user']

        if 'file' in self.cleaned_data and self.cleaned_data['file'] is not None:
            filecontent = self.cleaned_data['file']
            filename = self.cleaned_data['file'].name
        else:
            filecontent = None
            filename = None
        points = self.cleaned_data['points']
        comment = self.cleaned_data['comment']

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
    comment = forms.CharField(required=False)

    def __init__(self, data=None, *args, **kwargs):
        choices = kwargs.pop('choices')
        max_val = kwargs.pop('max_value')
        self.valid_files = kwargs.pop('valid_files')

        super(ZipForm, self).__init__(data, *args, **kwargs)

        self.fields['user'].choices = choices
        if 'initial' in kwargs and 'filename' in kwargs['initial']:
            self.name = kwargs['initial']['filename']

        self.fields['points'] = forms.IntegerField(min_value=0, required=False, max_value=max_val)

    def clean(self):
        cleaned_data = super(ZipForm, self).clean()
        self.name = cleaned_data['filename']

        if cleaned_data['user'] == 'None':
            cleaned_data['user'] = None
        else:
            cleaned_data['user'] = User.objects.get(pk=cleaned_data['user'])

        if cleaned_data['user'] is None:
            return cleaned_data

        if cleaned_data['filename'] not in self.valid_files:
            raise forms.ValidationError(_('Invalid filename %s') % cleaned_data['filename'])

        if cleaned_data['points'] is None:
            raise forms.ValidationError(_('Must have set points'))

        return cleaned_data


class BaseZipSet(BaseFormSet):

    def clean(self):
        if any(self.errors):
            return

        users = set()
        for form in self.forms:
            if 'user' is None:
                continue

            user = form.cleaned_data['user']
            if user and user in users:
                raise forms.ValidationError(_('Assigned 2 or more files to the same user.'))

            users.add(user)

    def save(self, archive_path, task):
        with zipfile.ZipFile(archive_path) as archive:
            for form in self:
                user = form.cleaned_data['user']

                if user is None:
                    continue

                fname = form.cleaned_data['filename']
                points = form.cleaned_data['points']
                comment = form.cleaned_data['comment']

                submit_review(archive.read(fname), os.path.basename(fname), task, user, points, comment)

        os.remove(archive_path)
