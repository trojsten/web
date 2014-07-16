# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .tasks import compile_task_statements
from trojsten.regal.tasks.models import Task


def notify_push(request):
    compile_task_statements.delay()
    return HttpResponse('')


def task_statement(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    template_data = {
        'task': task,
    }
    return render(
        request, 'trojsten/task_statements/view_task_statement.html', template_data
    )
