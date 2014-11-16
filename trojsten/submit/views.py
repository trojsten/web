# -*- coding: utf-8 -*-
# Create your views here.

import os
import xml.etree.ElementTree as ET

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.html import format_html

from sendfile import sendfile
from unidecode import unidecode

from trojsten.regal.contests.models import Round
from trojsten.regal.tasks.models import Task, Submit
from trojsten.submit.forms import SourceSubmitForm, DescriptionSubmitForm, TestableZipSubmitForm
from trojsten.submit.helpers import write_chunks_to_file, process_submit, get_path,\
    update_submit


@login_required
def view_submit(request, submit_id):
    submit = get_object_or_404(Submit, pk=submit_id)
    if submit.user != request.user and not Submit.objects.filter(pk=submit.pk, task__round__series__competition__organizers_group__user__pk=request.user.pk).exists():
        raise PermissionDenied()  # You shouldn't see other user's submits if you are not an organizer of the competition

    # For source submits, display testing results, source code and submit list.
    if submit.submit_type == Submit.SOURCE or submit.submit_type == Submit.TESTABLE_ZIP:
        if submit.testing_status == settings.SUBMIT_STATUS_IN_QUEUE:
            # check if submit wasn't tested yet
            update_submit(submit)
        template_data = {'submit': submit}
        protocol_path = submit.filepath.rsplit(
            '.', 1)[0] + settings.PROTOCOL_FILE_EXTENSION
        if os.path.exists(protocol_path):
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
            if runlog is not None:
                for runtest in runlog:
                    # Test log format in protocol is:
                    # name, resultCode, resultMsg, time, details
                    if runtest.tag != 'test':
                        continue
                    test = {}
                    test['name'] = runtest[0].text
                    test['result'] = runtest[2].text
                    test['time'] = runtest[3].text
                    details = runtest[4].text if len(runtest) > 4 else None
                    test['details'] = details
                    test['showDetails'] = details is not None and ('sample' in test['name'] or submit.submit_type == Submit.TESTABLE_ZIP)
                    tests.append(test)
            template_data['tests'] = tests
            template_data['have_tests'] = len(tests) > 0
        else:
            template_data['protocolReady'] = False  # Not tested yet!
        if os.path.exists(submit.filepath):
            # Source code available, display it!
            if submit.submit_type == Submit.SOURCE:
                template_data['fileReady'] = True
                with open(submit.filepath, "r") as submitfile:
                    data = submitfile.read()
                    template_data['data'] = data.decode('utf-8', 'replace')
            else:
                template_data['fileReady'] = False
                template_data['isZip'] = True
        else:
            template_data['fileReady'] = False  # File does not exist on server
        return render(
            request, 'trojsten/submit/view_submit.html', template_data
        )

    # For description submits, return submitted file.
    if submit.submit_type == Submit.DESCRIPTION:
        extension = os.path.splitext(submit.filepath)[1]
        # display .txt and .pdf files in browser, offer download for other files
        send_attachment = not extension.lower() in ['.pdf', '.txt']
        if os.path.exists(submit.filepath):
            return sendfile(
                request,
                submit.filepath,
                attachment=send_attachment,
            )
        else:
            raise Http404  # File does not exists, can't be returned


@login_required
def task_submit_page(request, task_id):
    '''View, ktory zobrazi formular na odovzdanie a zoznam submitov
    prave prihlaseneho cloveka pre danu ulohu'''
    task = get_object_or_404(Task, pk=task_id)
    template_data = {'task': task}
    return render(request, 'trojsten/submit/task_submit.html', template_data)


@login_required
def round_submit_page(request, round_id):
    '''View, ktorý zobrazí formuláre pre odovzdanie pre všetky úlohy
    z daného kola'''
    round = get_object_or_404(Round, pk=round_id)
    tasks = Task.objects.filter(round=round).order_by('number')
    template_data = {'round': round, 'tasks': tasks}
    return render(request, 'trojsten/submit/round_submit.html', template_data)


@login_required
def task_submit_post(request, task_id, submit_type):
    '''Spracovanie uploadnuteho submitu'''
    try:
        submit_type = int(submit_type)
    except ValueError:
        raise HttpResponseBadRequest

    # Raise Not Found when submitting non existent task
    task = get_object_or_404(Task, pk=task_id)

    # Raise Not Found when submitting non-submittable submit type
    if not task.has_submit_type(submit_type):
        raise Http404

    # Raise Not Found when not submitting through POST
    if request.method != "POST":
        raise Http404

    try:
        sfile = request.FILES['submit_file']
    except:
        # error will be reported from form validation
        pass

    # File will be sent to tester
    if submit_type == Submit.SOURCE or submit_type == Submit.TESTABLE_ZIP:
        if submit_type == Submit.SOURCE:
            form = SourceSubmitForm(request.POST, request.FILES)
        else:
            form = TestableZipSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            if submit_type == Submit.SOURCE:
                language = form.cleaned_data['language']
            else:
                language = '.zip'
            # Source submit's should be processed by process_submit()
            submit_id = process_submit(sfile, task, language, request.user)
            if not submit_id:
                messages.add_message(request, messages.ERROR,
                                     "Nepodporovaný formát súboru")
            else:
                # Source file-name is id.data
                sfiletarget = unidecode(os.path.join(get_path(
                    task, request.user), submit_id + '.data'))
                write_chunks_to_file(sfiletarget, sfile.chunks())
                sub = Submit(task=task,
                             user=request.user,
                             submit_type=submit_type,
                             points=0,
                             filepath=sfiletarget,
                             testing_status=settings.SUBMIT_STATUS_IN_QUEUE,
                             protocol_id=submit_id)
                sub.save()
                success_message = format_html(
                    "Úspešne si submitol program, výsledok testovania nájdeš "
                    "<a href='{}'>tu</a>",
                    reverse("view_submit", args=[sub.id])
                )
                messages.add_message(request, messages.SUCCESS, success_message)
        else:
            for field in form:
                for error in field.errors:
                    messages.add_message(request, messages.ERROR,
                                         "%s: %s" % (field.label, error))
        if 'redirect_to' in request.POST:
            return redirect(request.POST['redirect_to'])
        else:
            return redirect(
                reverse(
                    'task_submit_page', kwargs={'task_id': int(task_id)}
                )
            )


    # File won't be sent to tester
    elif submit_type == Submit.DESCRIPTION:
        form = DescriptionSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            # Description submit id's are currently timestamps
            from time import time
            submit_id = str(int(time()))
            # Description file-name should be: surname-id-originalfilename
            sfiletarget = unidecode(os.path.join(
                get_path(task, request.user),
                "%s-%s-%s" % (request.user.last_name, submit_id, sfile.name),
            ))
            write_chunks_to_file(sfiletarget, sfile.chunks())
            sub = Submit(task=task,
                         user=request.user,
                         submit_type=submit_type,
                         points=0,
                         testing_status=settings.SUBMIT_STATUS_IN_QUEUE,
                         filepath=sfiletarget)
            sub.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Úspešne sa ti podarilo submitnúť popis, "
                                 "po skončení kola ti ho vedúci opravia")
        else:
            for field in form:
                for error in field.errors:
                    messages.add_message(request, messages.ERROR,
                                         "%s: %s" % (field.label, error))

        if 'redirect_to' in request.POST:
            return redirect(request.POST['redirect_to'])
        else:
            return redirect(
                reverse(
                    'task_submit_page', kwargs={'task_id': int(task_id)}
                )
            )

    else:
        # Only Description and Source and Zip submitting is developed currently
        raise Http404
