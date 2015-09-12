from collections import defaultdict
from django.core.exceptions import PermissionDenied
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

from trojsten.submit.constants import SUBMIT_STATUS_REVIEWED
from trojsten.regal.tasks.models import Task, Submit
from trojsten.reviews.constants import REVIEW_POINTS_FILENAME, \
    REVIEW_COMMENT_FILENAME
from trojsten.reviews.helpers import (submit_download_filename,
                                      get_latest_submits_for_task, get_user_as_choices,
                                      submit_protocol_download_filename,
                                      submit_source_download_filename,
                                      submit_directory)

from trojsten.reviews.forms import ReviewForm, get_zip_form_set, reviews_upload_pattern, \
    UploadZipForm


def review_task(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    users = get_latest_submits_for_task(task)

    if not request.user.is_superuser and not \
            task.competition.organizers_group in request.user.groups.all():
        raise PermissionDenied

    if request.method == 'POST':
        form = UploadZipForm(request.POST, request.FILES)

        if form.is_valid():
            path_to_zip = form.save(request.user, task)

            if path_to_zip:
                request.session['review_archive'] = path_to_zip
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    _('Successfully uploaded a zip file.')
                )
                return redirect('admin:review_submit_zip', task.pk)
    else:
        form = UploadZipForm()

    context = {
        'task': task,
        'users': users,
        'form': form,
    }

    return render(
        request, 'admin/review_form.html', context
    )


def edit_review(request, task_pk, submit_pk):
    task = get_object_or_404(Task, pk=task_pk)
    submit = get_object_or_404(Submit, pk=submit_pk)

    if not request.user.is_superuser and not \
            task.competition.organizers_group in request.user.groups.all():
        raise PermissionDenied

    choices = get_user_as_choices(task)
    create = submit.testing_status != SUBMIT_STATUS_REVIEWED
    max_points = task.description_points

    if submit.task != task:
        raise Http404

    if request.method == 'POST':
        form = ReviewForm(request.POST,
                          request.FILES,
                          choices=choices,
                          max_value=max_points)

        if form.is_valid():
            form.save(submit, create)
            messages.add_message(
                request,
                messages.SUCCESS,
                _('Successfully saved the review'),
            )
            return redirect('admin:review_task', task.pk)
    else:
        form = ReviewForm(choices=choices, max_value=max_points, initial={
            'points': int(submit.points),
            'comment': submit.reviewer_comment,
            'user': submit.user_id
        })

    context = {
        'task': task,
        'submit': submit,
        'form': form,
        'create': create,
    }

    return render(
        request, 'admin/review_edit.html', context
    )


def submit_download(request, submit_pk):
    submit = get_object_or_404(Submit, pk=submit_pk)
    name = submit_download_filename(submit)

    if not request.user.is_superuser and not \
            submit.task.competition.organizers_group \
                    in request.user.groups.all():
        raise PermissionDenied

    if not os.path.isfile(submit.filepath):
        raise Http404

    return sendfile(request, submit.filepath, attachment=True, attachment_filename=name)


def download_latest_submits(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    submits = get_latest_submits_for_task(task).values()

    if not request.user.is_superuser and not \
            task.competition.organizers_group in request.user.groups.all():
        raise PermissionDenied

    path = os.path.join(settings.SUBMIT_PATH, 'reviews')
    if not os.path.isdir(path):
        os.makedirs(path)
        os.chmod(path, 0777)

    path = os.path.join(path, 'Uloha-%s-%s-%s.zip' %
                        (slugify(task.name), int(time()), slugify(request.user.username)))

    errors = []

    with zipfile.ZipFile(path, 'w') as zipper:
        for user in submits:
            submit = user['description']
            description_submit_id = submit.pk
            if not os.path.isfile(submit.filepath):
                errors += [_('Missing file of user %s') % submit.user.get_full_name()]
            else:
                zipper.write(submit.filepath, submit_download_filename(submit))
            last_review_points = user['review'].points if 'review' in user else 0
            last_review_comment = user['review'].reviewer_comment if 'review' in user else ''
            zipper.writestr(submit_directory(submit) + REVIEW_POINTS_FILENAME,
                            str(last_review_points))
            zipper.writestr(submit_directory(submit) + REVIEW_COMMENT_FILENAME,
                            str(last_review_comment))

            if 'sources' in user:
                for submit in user['sources']:
                    if not os.path.isfile(submit.filepath):
                        errors += [_('Missing source file of user %s') % submit.user.get_full_name()]
                    else:
                        zipper.write(submit.filepath, submit_source_download_filename(submit, description_submit_id))
                    if not os.path.isfile(submit.protocol_path):
                        errors += [_('Missing protocol file of user %s') % submit.user.get_full_name()]
                    else:
                        zipper.write(submit.protocol_path, submit_protocol_download_filename(submit, description_submit_id))

        if errors:
            zipper.writestr("errors.txt", "\n".join(errors).encode())

    return sendfile(request, path, attachment=True)


def zip_upload(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    name = request.session.get('review_archive', None)

    if name is None:
        raise Http404

    if not request.user.is_superuser and not \
            task.competition.organizers_group in request.user.groups.all():
        raise PermissionDenied

    try:
        archive = zipfile.ZipFile(name)
    except (zipfile.BadZipfile, IOError), e:
        messages.add_message(request, messages.ERROR, _('Problems with uploaded zip'))
        return redirect('admin:review_task', task.pk)

    with archive:
        filelist = archive.namelist()

        users = [(None, _('Ignore'))] + get_user_as_choices(task)
        initial = [{'filename': file} for file in filelist]
        user_data = defaultdict(dict)

        for form_data in initial:
            match = reviews_upload_pattern.match(form_data['filename'])
            if not match:
                continue

            pk = match.group('submit_pk')
            if Submit.objects.filter(pk=pk).exists():
                user_pk = Submit.objects.get(pk=pk).user.pk
                user_data[user_pk]['user'] = user_pk
                if match.group('filename') == REVIEW_POINTS_FILENAME:
                    try:
                        text = archive.read(form_data['filename'])
                        points_num = int(text)
                        user_data[user_pk]['points'] = points_num
                    except:
                        pass
                elif match.group('filename') == REVIEW_COMMENT_FILENAME:
                    try:
                        user_data[user_pk]['comment'] = archive.read(form_data['filename'])
                    except:
                        pass
                else:
                    user_data[user_pk]['filename'] = form_data['filename']

    initial = [user_data[user] for user in user_data]
    files = set([f['filename'] for f in initial])
    ZipFormSet = get_zip_form_set(
        choices=users, max_value=task.description_points, files=files, extra=0)

    if request.method == 'POST':
        formset = ZipFormSet(request.POST)

        if formset.is_valid():
            formset.save(name, task)

            request.session.pop('review_archive')
            messages.add_message(
                request,
                messages.SUCCESS,
                _("Successfully finished reviewing this task!")
            )
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
