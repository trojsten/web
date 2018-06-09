# -*- coding: utf-8 -*-
# Create your views here.

import json
import os
import xml.etree.ElementTree as ET

import six
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import (Http404, HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response as APIResponse
from sendfile import sendfile
from unidecode import unidecode

from trojsten.contests.models import Competition, Round, Task
from trojsten.submit.forms import (DescriptionSubmitForm, SourceSubmitForm,
                                   TestableZipSubmitForm)
from trojsten.submit.helpers import (get_path, process_submit, update_submit,
                                     write_chunks_to_file, get_description_file_path)
from trojsten.submit.templatetags.submit_parts import submitclass
from . import constants
from .constants import VIEWABLE_EXTENSIONS
from .models import Submit
from .serializers import ExternalSubmitSerializer


def protocol_data(protocol_path, force_show_details=False):
    template_data = {}
    if os.path.exists(protocol_path):
        template_data['protocolReady'] = True  # Tested, show the protocol
        try:
            tree = ET.parse(protocol_path)  # Protocol is in XML format
        except:  # noqa: E722 @FIXME
            # don't throw error if protocol is corrupted. (should only happen
            # while protocol is being uploaded)
            template_data['protocolReady'] = False
            return template_data
        clog = tree.find('compileLog')
        # Show compilation log if present
        template_data['compileLogPresent'] = clog is not None
        if clog is None:
            clog = ''
        else:
            clog = clog.text
        template_data['compileLog'] = clog
        tests = []
        runlog = tree.find('runLog')
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
                test['showDetails'] = details is not None and (
                    'sample' in test['name'] or force_show_details
                )
                tests.append(test)
        template_data['tests'] = tests
        template_data['have_tests'] = len(tests) > 0
    else:
        template_data['protocolReady'] = False  # Not tested yet!
    return template_data


@login_required
def view_reviewer_comment(request, submit_id):
    submit = get_object_or_404(Submit, pk=submit_id)
    if submit.user != request.user and not Submit.objects.filter(
            pk=submit.pk,
            task__round__semester__competition__organizers_group__user__pk=request.user.pk).exists():
        raise PermissionDenied()
        # You shouldn't see other user's submits if you are not an organizer
        # of the competition

    return HttpResponse(submit.rendered_comment)


@login_required
def view_protocol(request, submit_id):
    submit = get_object_or_404(Submit, pk=submit_id)
    if submit.user != request.user and not Submit.objects.filter(
            pk=submit.pk,
            task__round__semester__competition__organizers_group__user__pk=request.user.pk).exists():
        raise PermissionDenied()
        # You shouldn't see other user's submits if you are not an organizer
        # of the competition

    # For source submits, display testing results, source code and submit list.
    if (
        submit.submit_type == constants.SUBMIT_TYPE_SOURCE or
        submit.submit_type == constants.SUBMIT_TYPE_TESTABLE_ZIP
    ):
        protocol_path = submit.protocol_path
        is_organizer = request.user.is_in_group(submit.task.round.semester.competition.organizers_group)
        template_data = protocol_data(
            protocol_path, submit.submit_type == constants.SUBMIT_TYPE_TESTABLE_ZIP or is_organizer
        )
        template_data['submit'] = submit
        template_data['submit_verbose_response'] = constants.SUBMIT_VERBOSE_RESPONSE
        return render(
            request, 'trojsten/submit/protocol.html', template_data
        )
    else:
        raise Http404


@login_required
def view_submit(request, submit_id):
    submit = get_object_or_404(Submit, pk=submit_id)
    if submit.user != request.user and not Submit.objects.filter(
            pk=submit.pk,
            task__round__semester__competition__organizers_group__user__pk=request.user.pk).exists():
        raise PermissionDenied()
        # You shouldn't see other user's submits if you are not an organizer
        # of the competition

    # For source submits, display testing results, source code and submit list.
    if (
        submit.submit_type == constants.SUBMIT_TYPE_SOURCE or
        submit.submit_type == constants.SUBMIT_TYPE_TESTABLE_ZIP
    ):
        template_data = {
            'submit': submit,
            'source': True,
            'submit_verbose_response': constants.SUBMIT_VERBOSE_RESPONSE
        }
        protocol_path = submit.protocol_path
        is_organizer = request.user.is_in_group(submit.task.round.semester.competition.organizers_group)
        template_data.update(
            protocol_data(protocol_path, submit.submit_type == constants.SUBMIT_TYPE_TESTABLE_ZIP or is_organizer)
        )
        if os.path.exists(submit.filepath):
            # Source code available, display it!
            if submit.submit_type == constants.SUBMIT_TYPE_SOURCE:
                template_data['fileReady'] = True
                with open(submit.filepath, 'rb') as submitfile:
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
    elif submit.submit_type == constants.SUBMIT_TYPE_DESCRIPTION:
        extension = os.path.splitext(submit.filepath)[1]
        # display .txt and .pdf files in browser, offer download for other files
        send_attachment = extension.lower() not in VIEWABLE_EXTENSIONS
        if os.path.exists(submit.filepath):
            return sendfile(
                request,
                submit.filepath,
                attachment=send_attachment,
            )
        else:
            raise Http404  # File does not exists, can't be returned

    else:
        return render(
            request, 'trojsten/submit/view_submit.html', {
                'submit': submit,
                'source': False,
            }
        )


@login_required
def task_submit_page(request, task_id):
    """View, ktory zobrazi formular na odovzdanie a zoznam submitov
    prave prihlaseneho cloveka pre danu ulohu"""
    task = get_object_or_404(Task, pk=task_id)
    template_data = {'task': task}
    return render(request, 'trojsten/submit/task_submit.html', template_data)


@login_required
def round_submit_page(request, round_id):
    """View, ktorý zobrazí formuláre pre odovzdanie pre všetky úlohy
    z daného kola"""
    round = get_object_or_404(Round, pk=round_id)
    template_data = {'round': round}
    return render(request, 'trojsten/submit/round_submit.html', template_data)


@login_required
def active_rounds_submit_page(request):
    rounds = Round.objects.active_visible(request.user).order_by('end_time')
    competitions = Competition.objects.current_site_only()
    template_data = {
        'rounds': rounds,
        'competitions': competitions,
    }
    return render(
        request,
        'trojsten/submit/active_rounds_submit.html',
        template_data,
    )


@login_required
def all_submits_page(request, submit_type):
    submits_query_set = Submit.objects.filter(
        user=request.user, submit_type=submit_type,
        task__round__semester__competition__sites__in=[settings.SITE_ID],
    ).select_related(
        'task__round', 'task__round__semester', 'task__round__semester__competition',
    ).order_by(
        'task__round__semester__competition', '-task__round__semester__year', '-task__round__semester__number',
        '-task__round__number', 'task__number', 'submit_type', '-time'
    ).distinct(
        'task__round__semester__competition', 'task__round__semester__year', 'task__round__semester__number',
        'task__round__number', 'task__number', 'submit_type',
    )
    competitions = [None]
    semesters = {}
    all_submits = {}
    for submit in submits_query_set:
        competition = submit.task.round.semester.competition
        semester = submit.task.round.semester
        if competition != competitions[-1]:
            competitions.append(competition)
            all_submits[competition] = {}
            semesters[competition] = [None]
        if semester != semesters[competition][-1]:
            semesters[competition].append(semester)
            all_submits[competition][semester] = {}
            for round in semester.round_set.all():
                all_submits[competition][semester][round] = []
        all_submits[competition][semester][submit.task.round].append(submit)

    context = {
        'all_submits': all_submits,
        'competitions': competitions[1:],
        'all_semesters': semesters,
        'IN_QUEUE': constants.SUBMIT_STATUS_IN_QUEUE,
        'submit_type': submit_type,
        'DESCRIPTION': constants.SUBMIT_TYPE_DESCRIPTION,
    }

    return render(
        request,
        'trojsten/submit/all_submits_page.html',
        context
    )


@login_required
def all_submits_description_page(request):
    return all_submits_page(request, constants.SUBMIT_TYPE_DESCRIPTION)


@login_required
def all_submits_source_page(request):
    return all_submits_page(request, constants.SUBMIT_TYPE_SOURCE)


def receive_protocol(request, protocol_id):
    submit = get_object_or_404(Submit, protocol_id=protocol_id)
    update_submit(submit)
    return HttpResponse('')


#  @login_required
def poll_submit_info(request, submit_id):
    submit = get_object_or_404(Submit, pk=submit_id)
    if submit.user != request.user and not Submit.objects.filter(
            pk=submit.pk,
            task__round__semester__competition__organizers_group__user__pk=request.user.pk).exists():
        # You shouldn't see other user's submits if you are not an organizer of the competition
        raise PermissionDenied()

    if not submit.tested:  # try to find and parse protocol with each poll
        update_submit(submit)

    return HttpResponse(json.dumps({
        'tested': submit.tested,
        'response_verbose': six.text_type(submit.tester_response_verbose),
        'response': submit.tester_response,
        'points': float(submit.points),
        'class': submitclass(submit),
    }), content_type='application/json; charset=utf-8')


@login_required
def task_submit_post(request, task_id, submit_type):
    """Spracovanie uploadnuteho submitu"""
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
    if request.method != 'POST':
        raise Http404

    try:
        sfile = request.FILES['submit_file']
    except:  # noqa: E722 @FIXME
        # error will be reported from form validation
        pass

    # File will be sent to tester
    if (
        submit_type == constants.SUBMIT_TYPE_SOURCE or
        submit_type == constants.SUBMIT_TYPE_TESTABLE_ZIP
    ):
        if submit_type == constants.SUBMIT_TYPE_SOURCE:
            form = SourceSubmitForm(request.POST, request.FILES)
        else:
            form = TestableZipSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            if submit_type == constants.SUBMIT_TYPE_SOURCE:
                language = form.cleaned_data['language']
            else:
                language = '.zip'
            # Source submit's should be processed by process_submit()
            submit_id = process_submit(sfile, task, language, request.user)
            if not submit_id:
                messages.add_message(request, messages.ERROR,
                                     'Nepodporovaný formát súboru')
            else:
                # Source file-name is id.data
                sfiletarget = unidecode(os.path.join(get_path(
                    task, request.user), submit_id + constants.SUBMIT_SOURCE_FILE_EXTENSION))
                write_chunks_to_file(sfiletarget, sfile.chunks())
                sub = Submit(task=task,
                             user=request.user,
                             submit_type=submit_type,
                             points=0,
                             filepath=sfiletarget,
                             testing_status=constants.SUBMIT_STATUS_IN_QUEUE,
                             protocol_id=submit_id)
                sub.save()
                success_message = format_html(
                    'Úspešne si submitol program, výsledok testovania nájdeš '
                    '<a href="{}">tu</a>',
                    reverse('view_submit', args=[sub.id])
                )
                messages.add_message(request, messages.SUCCESS, success_message)
        else:
            for field in form:
                for error in field.errors:
                    messages.add_message(request, messages.ERROR,
                                         '%s: %s' % (field.label, error))
        if 'redirect_to' in request.POST and request.POST['redirect_to']:
            return redirect(request.POST['redirect_to'])
        else:
            return redirect(
                reverse(
                    'task_submit_page', kwargs={'task_id': int(task_id)}
                )
            )

    # File won't be sent to tester
    elif submit_type == constants.SUBMIT_TYPE_DESCRIPTION:
        if request.user.is_competition_ignored(task.round.semester.competition):
            return HttpResponseForbidden()
        form = DescriptionSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            sfiletarget = get_description_file_path(sfile, request.user, task)
            write_chunks_to_file(sfiletarget, sfile.chunks())
            sub = Submit(task=task,
                         user=request.user,
                         submit_type=submit_type,
                         points=0,
                         testing_status=constants.SUBMIT_STATUS_IN_QUEUE,
                         filepath=sfiletarget)
            sub.save()
            if task.round.can_submit:
                messages.add_message(request, messages.SUCCESS,
                                     _('You have successfully submitted your description, '
                                       'it will be reviewed after the round finishes.'))
            else:
                messages.add_message(request, messages.WARNING,
                                     _('You have submitted your description after the deadline. '
                                       'It is not counted in results.'))
        else:
            for field in form:
                for error in field.errors:
                    messages.add_message(request, messages.ERROR,
                                         '%s: %s' % (field.label, error))

        if 'redirect_to' in request.POST and request.POST['redirect_to']:
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


@api_view(['POST'])
@permission_classes([])
def external_submit(request):
    serializer = ExternalSubmitSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    validated = serializer.validated_data

    submit = Submit(
        task=validated['token'].task,
        user=validated['user'],
        points=validated['points'],
        submit_type=constants.SUBMIT_TYPE_EXTERNAL,
        testing_status=constants.SUBMIT_RESPONSE_OK,
    )
    submit.save()

    return APIResponse()
