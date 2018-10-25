# -*- coding: utf-8 -*-
# Create your views here.

import json
import logging
import os
import six
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import (Http404, HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import format_html
from django.utils.translation import ugettext as _
from judge_client import constants as judge_constants
from judge_client.client import ProtocolError
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.response import Response as APIResponse
from sendfile import sendfile
from unidecode import unidecode

from trojsten.contests import constants as contest_consts
from trojsten.contests.models import Competition, Round, Task
from trojsten.submit.forms import (DescriptionSubmitForm, SourceSubmitForm,
                                   TestableZipSubmitForm)
from trojsten.submit.helpers import (get_description_file_path, get_path,
                                     parse_result_and_points_from_protocol,
                                     process_submit, write_chunks_to_file)
from trojsten.submit.templatetags.submit_parts import submitclass
from . import constants
from .constants import VIEWABLE_EXTENSIONS
from .models import Submit
from .serializers import ExternalSubmitSerializer

logger = logging.getLogger(__name__)
judge_client = settings.JUDGE_CLIENT


def protocol_data(submit, force_show_details=False):
    if not submit.protocol:  # Not tested yet!
        return {'protocolReady': False}
    try:
        protocol = judge_client.parse_protocol(submit.protocol, submit.task.source_points)
        template_data = {
            'protocolReady': True,
            'compileLogPresent': protocol.compile_log is not None,
            'compileLog': protocol.compile_log,
        }
        tests = [
            {
                'name': runtest.name,
                'result': runtest.result,
                'time': runtest.time,
                'details': runtest.details,
                'showDetails': runtest.details is not None and ('sample' in runtest.name or force_show_details),
            }
            for runtest in protocol.tests
        ]
        template_data['tests'] = tests
        template_data['have_tests'] = len(tests) > 0
        return template_data
    except ProtocolError:
        return {'protocolReady': False}


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
            submit.submit_type == constants.SUBMIT_TYPE_SOURCE
            or submit.submit_type == constants.SUBMIT_TYPE_TESTABLE_ZIP
    ):
        is_organizer = request.user.is_in_group(
            submit.task.round.semester.competition.organizers_group)
        template_data = protocol_data(
            submit, submit.submit_type == constants.SUBMIT_TYPE_TESTABLE_ZIP or is_organizer
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
            submit.submit_type == constants.SUBMIT_TYPE_SOURCE
            or submit.submit_type == constants.SUBMIT_TYPE_TESTABLE_ZIP
    ):
        template_data = {
            'submit': submit,
            'source': True,
            'submit_verbose_response': constants.SUBMIT_VERBOSE_RESPONSE
        }
        is_organizer = request.user.is_in_group(
            submit.task.round.semester.competition.organizers_group)
        template_data.update(
            protocol_data(
                submit,
                submit.submit_type == constants.SUBMIT_TYPE_TESTABLE_ZIP or is_organizer
            )
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


@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
def upload_protocol(request):
    if not request.user.has_perm('old_submit.change_submit'):
        raise PermissionDenied()
    protocol_id = request.POST.get('submit_id')
    protocol_content = request.POST.get('protocol')
    if not protocol_id or not protocol_content:
        logger.warning('Missing submit_id or protocol.\n%s' % request.POST)
        return HttpResponse()
    try:
        submit = Submit.objects.get(protocol_id=protocol_id)
    except Submit.DoesNotExist:
        logger.warning('Invalid protocol id: %s' % protocol_id)
        return HttpResponse()
    submit.protocol = protocol_content
    result, points = parse_result_and_points_from_protocol(submit)
    if result is not None:
        submit.tester_response = result
        submit.points = points
        submit.testing_status = constants.SUBMIT_STATUS_FINISHED
    submit.save()
    return HttpResponse()


#  @login_required
def poll_submit_info(request, submit_id):
    submit = get_object_or_404(Submit, pk=submit_id)
    if submit.user != request.user and not Submit.objects.filter(
            pk=submit.pk,
            task__round__semester__competition__organizers_group__user__pk=request.user.pk).exists():
        # You shouldn't see other user's submits if you are not an organizer of the competition
        raise PermissionDenied()

    return HttpResponse(json.dumps({
        'tested': submit.tested,
        'response_verbose': six.text_type(submit.tester_response_verbose),
        'response': submit.tester_response,
        'points': float(submit.points),
        'class': submitclass(submit),
    }), content_type='application/json; charset=utf-8')


def send_notification_email(submit, task_id, submit_type):
    send_mail(
        _('[Trojstenweb] User submission detected'),
        (_('{name} submitted solution to task {task}\n\n')
         + (_('Link for reviewing: {review_link}\n\n') if submit_type == constants.SUBMIT_TYPE_DESCRIPTION else '')
         + _('Submit link: {submit_link}\n\n'
         + 'This is an automated response, do not reply')).format(
            name=submit.user.get_full_name(),
            task=submit.task,
            submit_link=Site.objects.get_current().domain + reverse('admin:old_submit_submit_change',
                                                                    args=(submit.id,)),
            review_link=Site.objects.get_current().domain + reverse('admin:review_edit',
                                                                    args=(task_id, submit.id))
        ),
        settings.DEFAULT_FROM_EMAIL,
        [org.email for org in submit.task.get_assigned_people_for_role(
            contest_consts.TASK_ROLE_REVIEWER)]
    )


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
            submit_type == constants.SUBMIT_TYPE_SOURCE
            or submit_type == constants.SUBMIT_TYPE_TESTABLE_ZIP
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
                if task.email_on_code_submit:
                    send_notification_email(sub, task_id, submit_type)

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
            if task.email_on_desc_submit:
                send_notification_email(sub, task_id, submit_type)

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
        testing_status=judge_constants.SUBMIT_RESPONSE_OK,
    )
    submit.save()
    return APIResponse()
