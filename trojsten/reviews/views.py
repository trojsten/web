from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib import messages

from trojsten.regal.tasks.models  import Task, Submit
from trojsten.regal.people.models import User
from trojsten.submit.helpers import save_file, get_path

from trojsten.reviews.helpers import submit_review, submit_readable_name, get_latest_submits_by_task
from trojsten.reviews.forms import ReviewForm

import os
import zipfile
import io

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
                #not implemented
                raise Http404

            else:    
                if user == 'None':
                    try:
                        print int(filename.split('-')[1])
                        user = Submit.objects.get(pk=int(filename.split('-')[1])).user
                    except KeyError:
                        messages.add_message(request, messages.ERROR, "Auto failed")
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


# Na toto by sa mohol pozriet niekto kto vie SQL
# dorobit filtrovanie veducich, a pod ...

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


