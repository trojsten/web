from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from trojsten.regal.tasks.models import Task, Submit
from django import forms

def task_view (request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    users = get_users(task)

    template_data = {
        'task': task,
        'users': users,
    }

    return render (
        request, "admin/review_form.html", template_data
    )

def task_user_view (request, task_pk, user_pk):
    task = get_object_or_404(Task, pk=task_pk)

    submits = task.submit_set.filter(submit_type=Submit.DESCRIPTION)

    if user_pk != "all":
        submits = submits.filter(user=user_pk)

    return HttpResponse("<br>".join([str(submit) for submit in submits]))

def get_users (task):
    qset = task.submit_set.filter(submit_type=Submit.DESCRIPTION).distinct("user").select_related("user", "user__username")
    return [{"pk": x.user.pk, "username": x.user.username} for x in qset]

def submit_download_view (request, submit_pk):
	submit = get_object_or_404(Submit, pk=submit_pk)
	name = "%s_%s_%s" % (str(submit.user.username), str(submit.pk), submit.filename.split("-")[-1])

	response = HttpResponse(open(submit.filepath).read(), content_type='application/force-download')
	response['Content-Disposition'] = 'attachment; filename=' + name
	return response