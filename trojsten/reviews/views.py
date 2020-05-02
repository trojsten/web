import os.path
import zipfile
from collections import OrderedDict
from time import time

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.forms import formset_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from sendfile import sendfile

from trojsten.contests.models import Task
from trojsten.reviews.constants import (
    RE_FILENAME,
    RE_SUBMIT_PK,
    REVIEW_COMMENT_FILENAME,
    REVIEW_ERRORS_FILENAME,
    REVIEW_POINTS_FILENAME,
)
from trojsten.reviews.forms import (
    BasePointForm,
    BasePointFormSet,
    ReviewForm,
    UploadZipForm,
    get_zip_form_set,
    reviews_upload_pattern,
)
from trojsten.reviews.helpers import (
    get_latest_submits_for_task,
    get_user_as_choices,
    submit_directory,
    submit_download_filename,
    submit_protocol_download_filename,
    submit_source_download_filename,
)
from trojsten.submit.constants import SUBMIT_STATUS_REVIEWED
from trojsten.submit.models import Submit


def review_task(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    PointsFormSet = formset_factory(BasePointForm, formset=BasePointFormSet, extra=0)

    if (
        not request.user.is_superuser
        and task.round.semester.competition.organizers_group not in request.user.groups.all()
    ):
        raise PermissionDenied

    form = None
    form_set = None

    if request.method == "POST":
        if request.POST.get("Upload", None):
            form = UploadZipForm(request.POST, request.FILES)
            if form.is_valid():
                path_to_zip = form.save(request.user, task)

                if path_to_zip:
                    request.session["review_archive"] = path_to_zip
                    messages.add_message(
                        request, messages.SUCCESS, _("Successfully uploaded a zip file.")
                    )
                    return redirect("admin:review_submit_zip", task.pk)
        if "points_submit" in request.POST:
            form_set = PointsFormSet(
                request.POST, form_kwargs={"max_points": task.description_points}
            )
            if form_set.is_valid():
                form_set.save(task)
                messages.add_message(
                    request, messages.SUCCESS, _("Points and comments were successfully updated.")
                )
                return redirect("admin:review_task", task.pk)

    users = get_latest_submits_for_task(task)
    users_list = list(users.keys())

    if not form:
        form = UploadZipForm()
    if not form_set:
        data = []
        for user in users_list:
            value = users[user]
            form_data = {"user": user}
            if "review" in value:
                form_data["points"] = value["review"].points
                form_data["reviewer_comment"] = value["review"].reviewer_comment
            data.append(form_data)
        form_set = PointsFormSet(initial=data, form_kwargs={"max_points": task.description_points})
    for i in range(0, len(users_list)):
        users[users_list[i]]["form"] = form_set.forms[i]

    context = {"task": task, "users": users, "form": form, "form_set": form_set}

    return render(request, "admin/review_form.html", context)


def edit_review(request, task_pk, submit_pk):
    task = get_object_or_404(Task, pk=task_pk)
    submit = get_object_or_404(Submit, pk=submit_pk)

    if (
        not request.user.is_superuser
        and task.round.semester.competition.organizers_group not in request.user.groups.all()
    ):
        raise PermissionDenied

    choices = get_user_as_choices(task)
    create = submit.testing_status != SUBMIT_STATUS_REVIEWED
    max_points = task.description_points

    if submit.task != task:
        raise Http404

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES, choices=choices, max_value=max_points)

        if form.is_valid():
            form.save(submit, create)
            messages.add_message(request, messages.SUCCESS, _("Successfully saved the review"))
            return redirect("admin:review_task", task.pk)
    else:
        form = ReviewForm(
            choices=choices,
            max_value=max_points,
            initial={
                "points": int(submit.points),
                "comment": submit.reviewer_comment,
                "user": submit.user_id,
            },
        )

    context = {"task": task, "submit": submit, "form": form, "create": create}

    return render(request, "admin/review_edit.html", context)


def submit_download(request, submit_pk):
    submit = get_object_or_404(Submit, pk=submit_pk)
    name = submit_download_filename(submit)

    if (
        not request.user.is_superuser
        and submit.task.round.semester.competition.organizers_group not in request.user.groups.all()
    ):
        raise PermissionDenied

    if not os.path.isfile(submit.filepath):
        raise Http404

    return sendfile(request, submit.filepath, attachment=True, attachment_filename=name)


def download_all_submits(request, task_pk, download_reviews=False):
    task = get_object_or_404(Task, pk=task_pk)
    submits = get_latest_submits_for_task(task).values()

    if (
        not request.user.is_superuser
        and task.round.semester.competition.organizers_group not in request.user.groups.all()
    ):
        raise PermissionDenied

    path = os.path.join(settings.SUBMIT_PATH, "reviews")
    if not os.path.isdir(path):
        os.makedirs(path)
        os.chmod(path, 0o777)

    path = os.path.join(
        path,
        "Uloha-%s-%s-%s.zip" % (slugify(task.name), int(time()), slugify(request.user.username)),
    )

    errors = []

    with zipfile.ZipFile(path, "w") as zipper:
        for i, user in enumerate(submits):
            if "description" in user:
                submit = (
                    user["review"] if download_reviews and "review" in user else user["description"]
                )
                description_submit_id = submit.pk
                if not os.path.isfile(submit.filepath):
                    errors += [_("Missing file of user %s") % submit.user.get_full_name()]
                else:
                    zipper.write(submit.filepath, submit_download_filename(submit, i))
                last_review_points = str(int(user["review"].points)) if "review" in user else ""
                last_review_comment = user["review"].reviewer_comment if "review" in user else ""
                zipper.writestr(
                    submit_directory(submit, i) + REVIEW_POINTS_FILENAME, last_review_points
                )
                zipper.writestr(
                    submit_directory(submit, i) + REVIEW_COMMENT_FILENAME,
                    last_review_comment.encode("utf-8"),
                )

            if "sources" in user:
                for submit in user["sources"]:
                    if os.path.isfile(submit.filepath):
                        zipper.write(
                            submit.filepath,
                            submit_source_download_filename(submit, description_submit_id, i),
                        )
                    else:
                        errors += [
                            _("Missing source file of user %s") % submit.user.get_full_name()
                        ]
                    if submit.protocol:
                        zipper.writestr(
                            submit_protocol_download_filename(submit, description_submit_id, i),
                            submit.protocol,
                        )
                    else:
                        errors += [_("Missing protocol of user %s") % submit.user.get_full_name()]

        if errors:
            zipper.writestr(REVIEW_ERRORS_FILENAME, "\n".join(errors).encode("utf8"))

    return sendfile(request, path, attachment=True)


def download_latest_submits(request, task_pk):
    return download_all_submits(request, task_pk, False)


def download_latest_reviewed_submits(request, task_pk):
    return download_all_submits(request, task_pk, True)


def zip_upload(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    name = request.session.get("review_archive", None)

    if name is None:
        raise Http404

    if (
        not request.user.is_superuser
        and task.round.semester.competition.organizers_group not in request.user.groups.all()
    ):
        raise PermissionDenied

    try:
        archive = zipfile.ZipFile(name)
    except (zipfile.BadZipfile, IOError):
        messages.add_message(request, messages.ERROR, _("Problems with uploaded zip"))
        return redirect("admin:review_task", task.pk)

    with archive:
        filelist = archive.namelist()

        users = [("None", _("Ignore"))] + get_user_as_choices(task)
        initial = [{"filename": file} for file in filelist]
        user_data = OrderedDict()

        for form_data in initial:
            match = reviews_upload_pattern.match(form_data["filename"])
            if not match:
                continue

            pk = match.group(RE_SUBMIT_PK)
            extension = ".%s" % (match.group(RE_FILENAME).split(".")[-1])
            if Submit.objects.filter(pk=pk).exists():
                user_pk = Submit.objects.get(pk=pk).user.pk
                if user_pk not in user_data:
                    user_data[user_pk] = {}
                user_data[user_pk]["user"] = user_pk
                if match.group(RE_FILENAME) == REVIEW_POINTS_FILENAME:
                    try:
                        text = archive.read(form_data["filename"])
                        points_num = int(text)
                        user_data[user_pk]["points"] = points_num
                    except:  # noqa: E722 @FIXME
                        pass
                elif match.group(RE_FILENAME) == REVIEW_COMMENT_FILENAME:
                    try:
                        user_data[user_pk]["comment"] = archive.read(form_data["filename"])
                    except:  # noqa: E722 @FIXME
                        pass
                elif extension.lower() in settings.SUBMIT_DESCRIPTION_ALLOWED_EXTENSIONS:
                    user_data[user_pk]["filename"] = form_data["filename"]

    initial = [user_data[user] for user in user_data if "filename" in user_data[user]]
    files = set([f["filename"] for f in initial])
    ZipFormSet = get_zip_form_set(
        choices=users, max_value=task.description_points, files=files, extra=0
    )

    if request.method == "POST":
        formset = ZipFormSet(request.POST)

        if formset.is_valid():
            formset.save(name, task)

            request.session.pop("review_archive")
            messages.add_message(
                request, messages.SUCCESS, _("Successfully finished reviewing this task!")
            )
            return redirect("admin:review_task", task.pk)
    else:
        formset = ZipFormSet(initial=initial)

    archive.close()

    context = {"formset": formset, "task": task}
    return render(request, "admin/zip_upload.html", context)
