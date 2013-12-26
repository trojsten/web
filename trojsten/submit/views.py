# Create your views here.

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import models
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.conf import settings
from trojsten.regal.tasks.models import Task, Submit
from trojsten.regal.people.models import Person
from trojsten.submit.forms import SourceSubmitForm, DescriptionSubmitForm
from trojsten.submit.helpers import save_file, process_submit, get_path


@login_required
def task_submit_form(request, task_id):
    task = Task.objects.get(pk=task_id)
    if not task:
        raise Http404

    template_data = {}
    template_data['task'] = task
    template_data['has_source'] = False
    template_data['has_description'] = False
    task_types = task.task_type.split(',')
    if 'source' in task_types:
        sform = SourceSubmitForm()
        template_data['source_form'] = sform
        template_data['has_source'] = True
    if 'description' in task_types:
        dform = DescriptionSubmitForm()
        template_data['description_form'] = dform
        template_data['has_description'] = True

    return render_to_response('trojsten/submit/task_submit_form.html',
                              template_data,
                              context_instance=RequestContext(request))


@login_required
def task_submit_post(request, task_id, submit_type):
    task = Task.objects.get(pk=task_id)
    # Raise Not Found when submitting non existent task
    if not task:
        raise Http404

    # Raise Not Found when submitting non-submittable submit type
    if submit_type not in task.task_type.split(','):
        raise Http404

    # Raise Not Found when not submitting through POST
    if request.method != "POST":
        raise Http404

    person = request.user.person
    sfile = request.FILES['submit_file']

    if submit_type == 'source':
        form = SourceSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            language = form.cleaned_data['language']
            submit_id = process_submit(sfile, task, language, person.user)
            sfiletarget = get_path(
                task, request.user) + '/' + submit_id + '.data'
            save_file(sfile, sfiletarget)
            sub = Submit(task=task,
                         person=person,
                         submit_type=submit_type,
                         points=0,
                         filename=sfiletarget,
                         testing_status='in queue',
                         protocol_id=submit_id)
            sub.save()
            return redirect(reverse('task_submit_form', kwargs={'task_id': int(task_id)}))

    elif submit_type == 'description':
        form = DescriptionSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            from time import time
            submit_id = str(int(time()))
            sfiletarget = get_path(task, request.user) + '/' + \
                person.surname + '-' + submit_id + '-' + sfile.name
            save_file(sfile, sfiletarget)
            sub = Submit(task=task,
                         person=person,
                         submit_type=submit_type,
                         points=0,
                         filename=sfile.name)
            sub.save()
            return redirect(reverse('task_submit_form', kwargs={'task_id': int(task_id)}))

    else:
        # Only Description and Source submitting is developed currently
        raise Http404
