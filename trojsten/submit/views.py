# -*- coding: utf-8 -*-
# Create your views here.

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import models
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.conf import settings
from trojsten.regal.tasks.models import Task, Submit
from trojsten.regal.people.models import Person
from trojsten.submit.forms import SourceSubmitForm, DescriptionSubmitForm
from trojsten.submit.helpers import save_file, process_submit, get_path, update_submit
import os
import xml.etree.ElementTree as ET


@login_required
def view_submit(request, submit_id):
    submit = Submit.objects.get(pk=submit_id)
    if not submit:
        raise Http404  # Return 404 if no submit with such ID exists.
    if submit.person != request.user.person:
        raise PermissionDenied()  # You shouldn't see other user's submits.

    # For source submits, display testing results, source code and submit list.
    if submit.submit_type == 'source':
        if submit.testing_status == 'in queue':
            # check if submit wasn't tested yet
            update_submit(submit)
        task = submit.task
        template_data = {'submit': submit}
        # under submit information, there should be list of all your submits.
        template_data = add_task_info(template_data, task)
        template_data = add_submit_list(template_data, task, submit.person)
        protocol_path = submit.filepath.rsplit('.', 1)[0] + '.protokol'
        if not os.path.exists(protocol_path):
            template_data['protocolReady'] = False  # Not tested yet!
        else:
            template_data['protocolReady'] = True  # Tested, show the protocol
            tree = ET.parse(protocol_path)  # Protocol is in XML format
            clog = tree.find("compileLog")
            # Show compilation log if present
            template_data['compileLogPresent'] = clog is not None
            if clog is None:
                clog = ""
            else:
                clog = clog.text
            template_data['compileLog'] = clog
            tests = []
            runlog = tree.find("runLog")
            for runtest in runlog:
                # Test log format in protocol is:
                # name, resultCode, resultMsg, time, details
                if runtest.tag != 'test':
                    continue
                test = {}
                test['name'] = runtest[0].text
                test['result'] = runtest[2].text
                test['time'] = runtest[3].text
                tests.append(test)
            template_data['tests'] = tests
        if not os.path.exists(submit.filepath):
            template_data['fileReady'] = False  # File does not exist on server
        else:
            # Source code available, display it!
            template_data['fileReady'] = True
            with open(submit.filepath, "r") as submitfile:
                data = submitfile.read()
                template_data['data'] = data
        return render_to_response('trojsten/submit/view_submit.html',
                                  template_data,
                                  context_instance=RequestContext(request))

    # For description submits, return submitted file.
    if submit.submit_type == 'description':
        if not os.path.exists(submit.filepath):
            raise Http404  # File does not exists, can't be returned
        else:
            data = open(submit.filepath, "rb")
            response = HttpResponse(data)
            response['Content-Disposition'] = 'attachment; filename=' + \
                str(submit.filename())
            return response


def add_task_info(template_data, task):
    '''Prida do template_data informacie o task-u (jeho objekt a typy
    submitu) (prerequisite na form_data a submit_list)'''
    task_types = task.task_type.split(',')
    template_data['task'] = task
    template_data['has_source'] = 'source' in task_types
    template_data['has_description'] = 'description' in task_types
    return template_data


def add_form_data(template_data, task):
    '''Prida do template_data formulare na submit task-u, potom v
    template include submit_form.html prida formular na submitovanie'''
    task_types = task.task_type.split(',')
    if 'source' in task_types:
        sform = SourceSubmitForm()
        template_data['source_form'] = sform
    if 'description' in task_types:
        dform = DescriptionSubmitForm()
        template_data['description_form'] = dform
    return template_data


def add_submit_list(template_data, task, person):
    '''Prida do template_data zoznam submitov k nejakej ulohe od nejakeho
    cloveka, potom v template include submit_list.html prida ten zoznam
    do stranky'''
    submits = Submit.objects.filter(task=task, person=person)
    template_data['source'] = submits.filter(submit_type='source')
    template_data['description'] = submits.filter(submit_type='description')
    # Update submits which are not updated yet!
    for submit in template_data['source'].filter(testing_status='in queue'):
        update_submit(submit)
    return template_data


@login_required
def task_submit_form(request, task_id):
    '''View, ktory zobrazi iba formular na odovzdanie jednej ulohy'''
    task = Task.objects.get(pk=task_id)
    if not task:
        raise Http404

    template_data = {}
    template_data = add_task_info(template_data, task)
    template_data = add_form_data(template_data, task)

    return render_to_response('trojsten/submit/task_submit_form.html',
                              template_data,
                              context_instance=RequestContext(request))


@login_required
def task_submit_page(request, task_id):
    '''View, ktory zobrazi formular na odovzdanie a zoznam submitov
    prave prihlaseneho cloveka pre danu ulohu'''
    task = Task.objects.get(pk=task_id)
    if not task:
        raise Http404

    template_data = {}
    template_data = add_task_info(template_data, task)
    template_data = add_form_data(template_data, task)
    template_data = add_submit_list(template_data, task, request.user.person)

    return render_to_response('trojsten/submit/task_submit_page.html',
                              template_data,
                              context_instance=RequestContext(request))


@login_required
def task_submit_list(request, task_id):
    '''View, ktory zobrazi iba zoznam submitov jednej ulohy'''
    task = Task.objects.get(pk=task_id)
    if not task:
        raise Http404

    template_data = {}
    template_data = add_task_info(template_data, task)
    template_data = add_submit_list(template_data, task, request.user.person)

    return render_to_response('trojsten/submit/task_submit_list.html',
                              template_data,
                              context_instance=RequestContext(request))


@login_required
def task_submit_post(request, task_id, submit_type):
    '''Spracovanie uploadnuteho submitu'''
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
            # Source submit's should be processed by process_submit()
            submit_id = process_submit(sfile, task, language, person.user)
            # Source file-name is id.data
            sfiletarget = get_path(
                task, request.user) + '/' + submit_id + '.data'
            save_file(sfile, sfiletarget)
            sub = Submit(task=task,
                         person=person,
                         submit_type=submit_type,
                         points=0,
                         filepath=sfiletarget,
                         testing_status='in queue',
                         protocol_id=submit_id)
            sub.save()
            return redirect(reverse('task_submit_form', kwargs={'task_id': int(task_id)}))

    elif submit_type == 'description':
        form = DescriptionSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            # Description submit id's are currently timestamps
            from time import time
            submit_id = str(int(time()))
            # Description file-name should be: surname-id-originalfilename
            sfiletarget = get_path(task, request.user) + '/' + \
                person.surname + '-' + submit_id + '-' + sfile.name
            save_file(sfile, sfiletarget)
            sub = Submit(task=task,
                         person=person,
                         submit_type=submit_type,
                         points=0,
                         testing_status='in queue',
                         filepath=sfiletarget)
            sub.save()
            return redirect(reverse('task_submit_form', kwargs={'task_id': int(task_id)}))

    else:
        # Only Description and Source submitting is developed currently
        raise Http404
