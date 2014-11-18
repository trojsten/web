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

from trojsten.reviews.helpers import submit_review

reviews_upload_pattern = re.compile(
    r'(?P<lastname>[^_]*)_(?P<submit_pk>[0-9]+)_(?P<filename>.+\.[^.]+)'
)


class ReviewForm(forms.Form):
    file = forms.FileField(max_length=128)
    user = forms.ChoiceField()
    points = forms.IntegerField(min_value=0, required=False)

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        max_val = kwargs.pop('max_value')
        super(ReviewForm, self).__init__(*args, **kwargs)

        # setting max_value doesn't work
        self.fields['points'] = forms.IntegerField(min_value=0, max_value=max_val, required=False)
        self.fields['user'].choices = choices

    def clean(self):
        cleaned_data = super(ReviewForm, self).clean()

        if 'file' not in cleaned_data:
            return {}

        # Choice field nevie rozlisit 'None' a None, tak je to (a vsetko ine) string
        if cleaned_data['user'] == 'None':
            cleaned_data['user'] = None

        filename = cleaned_data['file'].name
        user_id = cleaned_data['user']
        points = cleaned_data['points']

        # It's zip upload ==> valid
        if filename.endswith('.zip') and cleaned_data['user'] is None:
            return cleaned_data

        # Try to parse user form filename
        filematch = reviews_upload_pattern.match(filename)

        if filematch:
            cleaned_data['file'].name = filematch.group('filename')

        try:
            if user_id is None:
                # needs to resolve user
                if not filematch:
                    raise forms.ValidationError(_('Could not resolve user from %s') % filename)

                # user (probably) resolvable
                submit_id = filematch.group('submit_pk')
                user_id = Submit.objects.get(pk=submit_id).user.pk

            cleaned_data['user'] = User.objects.get(pk=user_id)

        except Submit.DoesNotExist:
            # file name id was wrong
            raise forms.ValidationError(_('Could not resolve user from %s') % filename)

        except (User.DoesNotExist, ValueError):
            raise forms.ValidationError(_('User %s does not exists') % user_id)

        if points is None:
            raise forms.ValidationError(_('Points are required'))

        return cleaned_data

    def save(self, req_user, task):
        '''Vrati path k zipu alebo None (ak sa zip neuplodoval)'''

        user = self.cleaned_data['user']
        filecontent = self.cleaned_data['file']

        filename = self.cleaned_data['file'].name
        points = self.cleaned_data['points']

        if user is None and filename.endswith('.zip'):
            path = os.path.join(
                settings.SUBMIT_PATH, 'reviews', '%s_%s.zip' % (int(time()), req_user.username)
            )
            path = unidecode(path)
            write_chunks_to_file(path, filecontent.chunks())
            return path

        submit_review(filecontent, filename, task, user, points)
        return None


def get_zip_form_set(choices, max_value, files, *args, **kwargs):
    '''Creates ZipFormSet which has forms with filled-in choices'''

    ZipFormWithChoices = wraps(ZipForm)(
        partial(ZipForm, choices=choices, max_value=max_value, valid_files=files)
    )
    return formset_factory(ZipFormWithChoices, *args, formset=BaseZipSet, **kwargs)


class ZipForm(forms.Form):
    filename = forms.CharField(widget=HiddenInput())
    user = forms.ChoiceField()
    points = forms.IntegerField(min_value=0, required=False)

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

                submit_review(archive.read(fname), os.path.basename(fname), task, user, points)

        os.remove(archive_path)
