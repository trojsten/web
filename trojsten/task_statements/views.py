# -*- coding: utf-8 -*-

import os

from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.conf import settings

from sendfile import sendfile

from trojsten.regal.tasks.models import Task
from trojsten.regal.contests.models import Round, Competition
from trojsten.utils.utils import is_true


def _statement_view(request, task_id, solution=False):
    task = get_object_or_404(Task, pk=task_id)
    if not task.visible(request.user) or (solution and not task.solution_visible(request.user)):
        raise Http404
    template_data = {
        'task': task,
        'path': task.get_path(solution=solution),
    }
    if solution:
        template_data['statement_path'] = task.get_path(solution=False)
    return render(
        request,
        'trojsten/task_statements/view_{}_statement.html'.format(
            'solution' if solution else 'task'
        ),
        template_data,
    )


def task_statement(request, task_id):
    return _statement_view(request, task_id, solution=False)


def solution_statement(request, task_id):
    return _statement_view(request, task_id, solution=True)


def task_list(request, round_id):
    round = get_object_or_404(Round.objects.visible(request.user), pk=round_id)
    competitions = Competition.objects.current_site_only()
    template_data = {
        'round': round,
        'competitions': competitions,
    }
    return render(
        request,
        'trojsten/task_statements/list_tasks.html',
        template_data,
    )


def active_rounds_task_list(request):
    rounds = Round.objects.active_visible(request.user).order_by('end_time')
    competitions = Competition.objects.current_site_only()
    template_data = {
        'rounds': rounds,
        'competitions': competitions,
    }
    return render(
        request,
        'trojsten/task_statements/list_active_rounds_tasks.html',
        template_data,
    )


def view_pdf(request, round_id, solution=False):
    round = get_object_or_404(Round.objects.visible(request.user), pk=round_id)
    if solution and not round.solutions_are_visible_for_user(request.user):
        raise Http404
    path = round.get_pdf_path(solution)
    if os.path.exists(path):
        response = sendfile(request, path)
        response['Content-Disposition'] = 'inline; filename="%s"' % round.get_pdf_name(solution)
        return response
    else:
        raise Http404


def show_picture(request, type, task_id, picture):
    task = get_object_or_404(Task, pk=task_id)
    if not task.visible(request.user):
        raise Http404
    _, ext = os.path.splitext(picture)
    if ext not in settings.ALLOWED_PICTURE_EXT:
        raise Http404
    path = os.path.join(
        task.round.get_pictures_path(),
        picture,
    )
    if os.path.exists(path):
        return sendfile(request, path)
    else:
        raise Http404


def ajax_progressbar(request, round_id):
    round = get_object_or_404(Round.objects.visible(request.user), pk=round_id)
    template_data = {
        'round': round,
        'results': is_true(request.GET.get('results', False)),
    }
    return render(
        request,
        'trojsten/task_statements/ajax/progress.html',
        template_data,
    )
