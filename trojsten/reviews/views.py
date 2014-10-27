import os.path
import zipfile
import io
from time import time

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings

from trojsten.regal.tasks.models  import Task, Submit
from trojsten.regal.people.models import User
from trojsten.submit.helpers import save_file, get_path

from trojsten.reviews.helpers import submit_review, submit_readable_name, get_latest_submits_by_task
from trojsten.reviews.forms import ReviewForm, get_zip_form_set


def review_task_view (request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    max_points = task.description_points
    users = get_latest_submits_by_task(task)
    choices = [(None, "Auto / all")] + [(user.pk, user.username) for user in users]

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, choices=choices, max_value=max_points)

        if form.is_valid():
            user = form.cleaned_data["user"]
            filecontent = request.FILES["file"]
            filename = form.cleaned_data["file"].name
            points = form.cleaned_data["points"]

            if user == 'None' and filename.endswith(".zip"):
                path = os.path.join(settings.SUBMIT_PATH, "reviews", "%s-%s.zip" % (int(time()), request.user.pk))
                print filecontent.chunks()

                save_file(filecontent, path)

                request.session["review_archive"] = path
                return redirect ("admin:review_submit_zip", task.pk)

            if user == 'None':      
                try:
                    user = Submit.objects.get(pk=int(filename.split('-')[1])).user
                
                except Submit.DoesNotExist:
                    messages.add_message(request, messages.ERROR, "Auto failed")
                    return redirect("admin:review_task", task.pk)
            else:
                user = User.objects.get(pk=int(user))

            #TODO: add regex to check for Name-submitID-filename format

            fname = "".join(filename.split("-")[2:])
            submit_review(filecontent, filename, task, user, points)

            messages.add_message(request, messages.SUCCESS, "Uploaded file %s to %s" % (fname, user.last_name))

            return redirect("admin:review_task", task.pk)

    template_data = {
        'task': task,
        'users': users,
        'form' : ReviewForm(choices=choices, max_value=max_points),
    }

    return render (
        request, 'admin/review_form.html', template_data
    )


def submit_download_view (request, submit_pk):
    submit = get_object_or_404(Submit, pk=submit_pk)
    name = submit_readable_name(submit)

    response = HttpResponse(open(submit.filepath).read(), content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename=' + name

    return response


def download_latest_submits_view (request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    data = [data['description'] for data in get_latest_submits_by_task(task).values()]

    result = io.BytesIO()
    zipper = zipfile.ZipFile(result, 'w')

    for submit in data:
        zipper.write(submit.filepath, submit_readable_name(submit))

    zipper.close()
    result.seek(0)
    
    response = HttpResponse(result.read(), content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename=Uloha %s.zip' % task.name 
    return response

from django import forms
def zip_upload (request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    name = request.session.get("review_archive", None)
    try:
        data = zipfile.ZipFile(name)

    except (zipfile.BadZipfile, IOError):
        messages.add_message(request, messages.ERROR, "Problems with uploaded zip")
        return redirect ("admin:review_task", task.pk)

    users = [(None, "")] +  [(user.pk, user.username) for user in get_latest_submits_by_task(task)]
    initial =   [{
                    'filename': file, 
                } 
                for file in data.namelist()]   

    ZipFormSet = get_zip_form_set (users, task.description_points, extra=0, can_delete=True)
    formset = ZipFormSet (initial=initial)

    if request.method == 'POST':
        formset = ZipFormSet (request.POST)
        
        try:
            if not formset.is_valid(): raise forms.ValidationError("Jump out")
            names = data.namelist()

            for form in formset:
                user = form.cleaned_data["user"]
                filename = form.cleaned_data["filename"]
                points = form.cleaned_data["points"]

                if user == 'None': continue
                
                if not filename in names:
                    err = "Invalid filename %s" % filename
                    form._errors["__all__"] = form.error_class([err])
                    raise forms.ValidationError(err)

                user = User.objects.get(pk=int(user))
                submit_review (data.read(filename), os.path.split(filename)[1], task, user, points)

            
            return redirect("admin:review_task", task.pk)
        
        except forms.ValidationError:
            for form in formset:
                form.name = form.cleaned_data["filename"]

    template_data = {
        'formset': formset,
        'task': task
    } 
    return render (
        request, "admin/zip_upload.html", template_data
    )



