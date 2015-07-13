import os.path
import zipfile
from time import time

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify

from sendfile import sendfile

from trojsten.regal.tasks.models import Task, Submit
from trojsten.reviews.helpers import (submit_download_filename,
                                      get_latest_submits_for_task, get_user_as_choices,
                                      submit_protocol_download_filename,
                                      submit_source_download_filename)

from trojsten.reviews.forms import ReviewForm, get_zip_form_set, reviews_upload_pattern


def review_task(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    max_points = task.description_points

    users = get_latest_submits_for_task(task)
    choices = [("None", 'Auto / all')] + get_user_as_choices(task)

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, choices=choices, max_value=max_points)

        if form.is_valid():
            path_to_zip = form.save(request.user, task)

            if path_to_zip:
                request.session['review_archive'] = path_to_zip
                return redirect('admin:review_submit_zip', task.pk)

            messages.add_message(
                request, messages.SUCCESS,
                _('Uploaded file %(file)s to %(name)s') % {
                    'file': form.cleaned_data['file'].name,
                    'name': form.cleaned_data['user'].get_full_name(),
                }
            )

            return redirect('admin:review_task', task.pk)
    else:
        form = ReviewForm(choices=choices, max_value=max_points)

    context = {
        'task': task,
        'users': users,
        'form': form,
    }

    return render(
        request, 'admin/review_form.html', context
    )


def submit_download(request, submit_pk):
    submit = get_object_or_404(Submit, pk=submit_pk)
    name = submit_download_filename(submit)

    if not os.path.isfile(submit.filepath):
        raise Http404

    return sendfile(request, submit.filepath, attachment=True, attachment_filename=name)


def download_latest_submits(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    _submits = get_latest_submits_for_task(task).values()
    description_submits = [data['description'] for data in _submits]
    source_submits = [data['sources'] for data in _submits]

    path = os.path.join(settings.SUBMIT_PATH, 'reviews')
    if not os.path.isdir(path):
        os.makedirs(path)
        os.chmod(path, 0777)

    path = os.path.join(path, 'Uloha-%s-%s-%s.zip' %
                        (slugify(task.name), int(time()), slugify(request.user.username)))

    errors = []

    with zipfile.ZipFile(path, 'w') as zipper:
        for submit in description_submits:
            if not os.path.isfile(submit.filepath):
                errors += [_('Missing file of user %s') % submit.user.get_full_name()]
            else:
                zipper.write(submit.filepath, submit_download_filename(submit))

        for user_submits in source_submits:
            for submit in user_submits:
                if not os.path.isfile(submit.filepath):
                    errors += [_('Missing source file of user %s') % submit.user.get_full_name()]
                else:
                    zipper.write(submit.filepath, submit_source_download_filename(submit))
                if not os.path.isfile(submit.protocol_path):
                    errors += [_('Missing protocol file of user %s') % submit.user.get_full_name()]
                else:
                    zipper.write(submit.protocol_path, submit_protocol_download_filename(submit))

        if errors:
            zipper.writestr("errors.txt", "\n".join(errors).encode())

    return sendfile(request, path, attachment=True)


def zip_upload(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    name = request.session.get('review_archive', None)

    if name is None:
        raise Http404

    try:
        archive = zipfile.ZipFile(name)
    except (zipfile.BadZipfile, IOError), e:
        messages.add_message(request, messages.ERROR, _('Problems with uploaded zip'))
        return redirect('admin:review_task', task.pk)

    with archive:
        filelist = archive.namelist()

    users = [(None, _('Ignore'))] + get_user_as_choices(task)
    initial = [{'filename': file} for file in filelist]

    for form_data in initial:
        match = reviews_upload_pattern.match(form_data['filename'])
        if not match:
            continue

        pk = match.group('submit_pk')
        try:
            form_data['user'] = Submit.objects.get(pk=pk).user.pk
        except Submit.DoesNotExist:
            pass

    initial = [f for f in initial if 'user' in f]
    files = set([f['filename'] for f in initial])
    ZipFormSet = get_zip_form_set(
        choices=users, max_value=task.description_points, files=files, extra=0)

    if request.method == 'POST':
        formset = ZipFormSet(request.POST)

        if formset.is_valid():
            formset.save(name, task)

            request.session.pop('review_archive')
            return redirect('admin:review_task', task.pk)
    else:
        formset = ZipFormSet(initial=initial)

    archive.close()

    context = {
        'formset': formset,
        'task': task
    }
    return render(
        request, 'admin/zip_upload.html', context
    )
