# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from .tasks import compile_task_statements
from trojsten.regal.tasks.models import Task
from trojsten.regal.contests.models import Round
from .helpers import get_task_path, get_rounds_by_year,\
    get_pdf_path, get_latest_rounds_by_competition
from sendfile import sendfile


def notify_push(request, uuid):
    compile_task_statements.delay(uuid)
    return HttpResponse('')


def _statement_view(request, task_id, solution=False):
    task = get_object_or_404(Task, pk=task_id)
    path = get_task_path(task, solution=solution)
    if path is None:
        raise Http404
    template_data = {
        'task': task,
        'path': path
    }
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
    round = Round.objects.get(pk=round_id)
    other_rounds = get_rounds_by_year()
    template_data = {
        'round': round,
        'other_rounds': other_rounds,
    }
    return render(
        request,
        'trojsten/task_statements/list_tasks.html',
        template_data,
    )


def latest_task_list(request):
    rounds = get_latest_rounds_by_competition()
    other_rounds = get_rounds_by_year()
    template_data = {
        'rounds': rounds,
        'other_rounds': other_rounds,
    }
    return render(
        request,
        'trojsten/task_statements/list_latest_tasks.html',
        template_data,
    )


def view_pdf(request, round_id):
    round = Round.objects.get(pk=round_id)
    path = get_pdf_path(round)
    return sendfile(request, path)
