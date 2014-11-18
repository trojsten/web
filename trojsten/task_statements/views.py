# -*- coding: utf-8 -*-

import os

from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.conf import settings

from sendfile import sendfile

from trojsten.regal.tasks.models import Task
from trojsten.regal.contests.models import Round, Competition

from .tasks import compile_task_statements


def notify_push(request, uuid):
    compile_task_statements.delay(uuid)
    return HttpResponse('')


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
    competitions = Competition.objects.all()  # Todo: filter by site
    template_data = {
        'round': round,
        'competitions': competitions,
    }
    return render(
        request,
        'trojsten/task_statements/list_tasks.html',
        template_data,
    )


def latest_task_list(request):
    rounds = Round.objects.latest_visible(request.user)
    competitions = Competition.objects.all()  # Todo: filter by site
    template_data = {
        'rounds': rounds,
        'competitions': competitions,
    }
    return render(
        request,
        'trojsten/task_statements/list_latest_tasks.html',
        template_data,
    )


def view_pdf(request, round_id, solution=False):
    round = get_object_or_404(Round.objects.visible(request.user), pk=round_id)
    if solution and not round.solutions_are_visible_for_user(request.user):
        raise Http404
    path = round.get_pdf_path(solution)
    if os.path.exists(path):
        return sendfile(request, path)
    else:
        raise Http404


def show_picture(request, type, task_id, picture):
    task = get_object_or_404(Task, pk=task_id)
    if not task.visible(request.user):
        raise Http404
    _, ext = os.path.splitext(picture)
    if not ext in settings.ALLOWED_PICTURE_EXT:
        raise Http404
    path = os.path.join(
        task.round.get_pictures_path(),
        picture,
    )
    if os.path.exists(path):
        return sendfile(request, path)
    else:
        raise Http404
