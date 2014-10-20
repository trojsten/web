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
        request, 'admin/review_form.html', template_data
    )

def task_user_view (request, task_pk, user_pk):
    task = get_object_or_404(Task, pk=task_pk)
    submits = task.submit_set.filter(submit_type=Submit.DESCRIPTION)

    if user_pk != 'all':
        submits = submits.filter(user=user_pk)

    return HttpResponse('<br>'.join([str(submit) for submit in submits]))

# Na toto by sa mohol pozriet niekto kto vie SQL
# dorobit filtrovanie veducich, a pod ...

def get_users (task):
    des_submits = task.submit_set.filter(submit_type=Submit.DESCRIPTION, time__lt=task.round.end_time).select_related('user', 'user__username')
    rev_submits = task.submit_set.filter(submit_type=Submit.REVIEW).select_related('user', 'user__username')

    users = {}
    for submit in des_submits:
    	if not submit.user in users:
    		users[submit.user] = {'user':submit.user, 'description': submit}
    	
    	elif users[submit.user]['description'].time < submit.time:
    		users[submit.user]['description'] = submit

    for submit in rev_submits:
    	if not submit.user in users:
    		users[submit.user] = {'user':submit.user, 'review': submit}
    	
    	elif not 'review' in users[submit.user]:
    		users[submit.user]['review'] = submit

    	elif users[submit.user]['review'].time < submit.time:
    		users[submit.user]['review'] = submit




    return users

def submit_download_view (request, submit_pk):
    submit = get_object_or_404(Submit, pk=submit_pk)
    name = '%s_%s_%s' % (str(submit.user.username), str(submit.pk), submit.filename.split('-')[-1])

    response = HttpResponse(open(submit.filepath).read(), content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename=' + name

    return response