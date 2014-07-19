# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from .tasks import compile_task_statements
from trojsten.regal.tasks.models import Task
from django.conf import settings
import os


def _get_task_path(task, solution=False):
    task_file = '{}{}.html'.format(settings.TASK_STATEMENTS_PREFIX_TASK, task.number,)
    round_dir = '{}{}'.format(task.round.number, settings.TASK_STATEMENTS_SUFFIX_ROUND)
    year_dir = '{}{}'.format(task.round.series.year, settings.TASK_STATEMENTS_SUFFIX_YEAR)
    competition_name = task.round.series.competition.name
    path_type = settings.TASK_STATEMENTS_SUFFIX_SOLUTIONS if solution else settings.TASK_STATEMENTS_TASKS_DIR
    path = os.path.join(settings.TASK_STATEMENTS_PATH, competition_name, year_dir, round_dir, path_type, settings.TASK_STATEMENTS_HTML_DIR, task_file)
    print path
    if os.path.exists(path):
        return path


def notify_push(request, uuid):
    compile_task_statements.delay(uuid)
    return HttpResponse('')


def _statement_view(request, task_id, solution=False):
    task = get_object_or_404(Task, pk=task_id)
    path = _get_task_path(task, solution=solution)
    if path is None:
        raise Http404
    template_data = {
        'task': task,
        'path': path
    }
    return render(
        request, 'trojsten/task_statements/view_{}_statement.html'.format('solution' if solution else 'task'), template_data
    )


def task_statement(request, task_id):
    return _statement_view(request, task_id, solution=False)


def solution_statement(request, task_id):
    return _statement_view(request, task_id, solution=True)
