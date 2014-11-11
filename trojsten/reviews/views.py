import os.path
import zipfile
import io
import re
from time import time

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify

from sendfile import sendfile

from trojsten.regal.tasks.models  import Task, Submit
from trojsten.regal.people.models import User
from trojsten.submit.helpers import save_file, get_path

from trojsten.reviews.helpers import submit_review, submit_download_filename, get_latest_submits_by_task
from trojsten.reviews.forms import ReviewForm, get_zip_form_set

reviews_upload_pattern = re.compile(r"(?P<lastname>[^_]*)_(?P<submit_pk>[0-9]+)_(?P<filename>.+\.[^.]+)")

def review_task(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    max_points = task.description_points
    users = get_latest_submits_by_task(task)
    choices = [(None, "Auto / all")] + [(user.pk, user.username) for user in users]

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES, choices=choices, max_value=max_points)

        if form.is_valid():
            print ("Passed !")

            user = form.cleaned_data["user"]
            filecontent = request.FILES["file"]
            filename = form.cleaned_data["file"].name
            points = form.cleaned_data["points"]

            if user is None and filename.endswith(".zip"):
                path = os.path.join(settings.SUBMIT_PATH, "reviews", "%s_%s.zip" % (int(time()), request.user.pk))
                save_file(filecontent, path)

                request.session["review_archive"] = path
                return redirect("admin:review_submit_zip", task.pk)


            submit_review(filecontent, filename, task, user, points)
            messages.add_message(
                request, messages.SUCCESS, 
                _("Uploaded file %(file)s to %(fname)s %(lname)s") % {
                    "file": filename, "fname": user.first_name, "lname": user.last_name
                }
            )

            return redirect("admin:review_task", task.pk)
    else:
        form = ReviewForm(choices=choices, max_value=max_points)

    context = {
        "task": task,
        "users": users,
        "form" : form,
    }

    return render(
        request, "admin/review_form.html", context
    )


def submit_download(request, submit_pk):
    submit = get_object_or_404(Submit, pk=submit_pk)
    name = submit_download_filename(submit)

    return sendfile(request, submit.filepath, attachment=True, attachment_filename=name)


def download_latest_submits(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    submits = [data["description"] for data in get_latest_submits_by_task(task).values()]

    path = os.path.join(settings.SUBMIT_PATH, "reviews")
    if not os.path.isdir(path):
        os.makedirs(path)
        os.chmod(path, 0777)

    path = os.path.join(path, "Uloha-%s-%s-%s.zip" % (slugify(task.name), int(time()), request.user.username))

    with zipfile.ZipFile(path, "w") as zipper:
        for submit in submits:
            zipper.write(submit.filepath, submit_download_filename(submit))

    
    return sendfile(request, path, attachment=True)


def zip_upload(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    name = request.session.get("review_archive", None)
    
    if name is None: 
        raise Http404

    try:
        archive = zipfile.ZipFile(name)
    except (zipfile.BadZipfile, IOdError):
        messages.add_message(request, messages.ERROR, _("Problems with uploaded zip"))
        return redirect("admin:review_task", task.pk)

    users = [(None, "")] + [(user.pk, user.username) for user in get_latest_submits_by_task(task)]
    initial = [{"filename": file} for file in archive.namelist()] 

    for form_data in initial:
        match = reviews_upload_pattern.match(form_data["filename"])
        if not match: 
            continue

        pk = match.group("submit_pk")
        try:
            form_data["user"] = Submit.objects.get(pk=pk).user.pk
        except Submit.DoesNotExist:
            pass 

    ZipFormSet = get_zip_form_set(users, task.description_points, extra=0)
    formset = ZipFormSet(initial=initial)

    if request.method == "POST":
        formset = ZipFormSet(request.POST)
        
        if formset.is_valid():
            names = archive.namelist()
            valid = True

            for form in formset:
                if not form.cleaned_data["filename"] in names:
                    err = _("Invalid filename %(file)s") % {"file": filename}
                    form._errors["__all__"].append(form.error_class([err]))
                    
                    valid = False
                    continue

            if valid:
                for form in formset:
                    user = form.cleaned_data["user"]
                    filename = form.cleaned_data["filename"]
                    points = form.cleaned_data["points"]

                    if user == "None": 
                        continue

                    user = User.objects.get(pk=user)
                    submit_review(archive.read(filename), os.path.basename(filename), task, user, points)

                archive.close()
                os.remove(name)

                request.session.pop("review_archive")
                return redirect("admin:review_task", task.pk)
        
        for form in formset:
            form.name = form.cleaned_data["filename"]

    archive.close()            

    context = {
        "formset": formset,
        "task": task
    } 
    return render(
        request, "admin/zip_upload.html", context
    )
