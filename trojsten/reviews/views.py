from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
# -*- coding: utf-8 -*-
from django.contrib import messages

from trojsten.regal.tasks.models  import Task, Submit
from trojsten.regal.people.models import User
from trojsten.submit.helpers import save_file, get_path

from django import forms
import os
# the code will be later refractored to proper files

def submit_review (filecontent, filename, task, user, points):
    from time import time
    submit_id = str(int(time()))
    
    sfiletarget = os.path.join(
        get_path(task, user),
        "%s-%s-%s" % (user.last_name, submit_id, filename),
    )

    save_file(filecontent, sfiletarget)
    sub = Submit(task=task,
                 user=user,
                 submit_type=Submit.DESCRIPTION,
                 points=points,
                 testing_status=Submit.STATUS_REVIEWED,
                 filepath=sfiletarget)
    sub.save()




def review_task_view (request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    max_points = task.description_points
    users = get_latest_submits_by_task(task)
    choices = [(-1, "Auto"), (None, "All")] + [(user.pk, user.username) for user in users]

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, choices=choices, max_value=max_points)

        if form.is_valid():
            user = form.cleaned_data["user"]
            filecontent = request.FILES["file"]
            filename = form.cleaned_data["file"].name
            points = form.cleaned_data["points"]

            if user == None:
                #not implemented
                raise Http404
            else:    
                user = int(user)
                if user == -1:
                    try:
                        print int(filename.split('-')[1])
                        user = Submit.objects.get(pk=int(filename.split('-')[1])).user
                    except KeyError:
                        messages.add_message(request, messages.ERROR, "Auto failed")
                else:
                    user = User.objects.get(pk=user)
                    
                #TODO: add regex to check for Name-submitID-filename format

                fname = "".join(filename.split("-")[2:])
                submit_review(filecontent, filename, task, user, points)

                messages.add_message(request, messages.SUCCESS, "Uploadnute")

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

def get_latest_submits_by_task (task):
    des_submits = task.submit_set.filter(submit_type=Submit.DESCRIPTION, time__lt=task.round.end_time, testing_status="in queue").select_related('user', 'user__username')
    rev_submits = task.submit_set.filter(submit_type=Submit.DESCRIPTION, testing_status=Submit.STATUS_REVIEWED).select_related('user', 'user__username')

    users = {}
    for submit in des_submits:
        if not submit.user in users:
            users[submit.user] = {'description': submit}
        
        elif users[submit.user]['description'].time < submit.time:
            users[submit.user]['description'] = submit

    for submit in rev_submits:
        if not submit.user in users:
            users[submit.user] = {'review': submit}
        
        elif not 'review' in users[submit.user]:
            users[submit.user]['review'] = submit

        elif users[submit.user]['review'].time < submit.time:
            users[submit.user]['review'] = submit

    return users


def submit_readable_name (submit):
    return '%s-%s-%s' % (submit.user.last_name, submit.pk, "".join(submit.filename.split('-')[2:]))


def submit_download_view (request, submit_pk):
    submit = get_object_or_404(Submit, pk=submit_pk)
    name = submit_readable_name(submit)

    response = HttpResponse(open(submit.filepath).read(), content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename=' + name

    return response

import zipfile
import io

def download_latest_submits_view (request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    data = [data['description'] for data in get_latest_submits_by_task(task).values()]

    result = io.BytesIO()
    zipper = zipfile.ZipFile(result, 'w')

    for submit in data:
        zipper.write(submit.filepath, submit_readable_name(submit))

    zipper.close()
    result.seek(0)
    
    response = HttpResponse(result.read(),content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename=Uloha %s.zip' % task.name 
    return response


from django import forms

class ReviewForm (forms.Form):
    file = forms.FileField(max_length=128)
    user = forms.ChoiceField ()
    points = forms.IntegerField(min_value=0, required=False)

    def __init__ (self, *args, **kwargs):
        choices = kwargs.pop("choices")
        max_value = kwargs.pop("max_value")
        super(ReviewForm, self).__init__(*args, **kwargs)

        self.fields["user"].choices = choices
        self.fields["points"] = forms.IntegerField(min_value=0, max_value=max_value, required=False)
