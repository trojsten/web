# -*- coding: utf-8 -*-

import json
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import View

from sendfile import sendfile

from trojsten.regal.tasks.models import Task

from .constants import DATA_ROOT
from .models import LevelSolved, LevelSubmit
from .tasks import process_submit


@login_required()
def index(request):
    return sendfile(request, os.path.join(DATA_ROOT, "index.html"))


@login_required()
def levels(request):
    data = load_level_index()
    user = request.user

    sid = 0
    for serie in data["series"]:
        # Set whether serie is rated
        serie["rated"] = (
            is_task_rated(serie["task_ids"]["ksp"], user, False) or
            is_task_rated(serie["task_ids"]["prask"], user, True))
        del serie["task_ids"]
        # Set headers for all levels
        level_paths = serie["levels"]
        serie["levels"] = []
        lid = 0
        for path in level_paths:
            with open(os.path.join(DATA_ROOT, path)) as f:
                level = json.load(f)
            serie["levels"].append({
                "id": "s%dl%d" % (sid,lid),
                "name": level["name"],
                "description": level["briefing"],
                "solved": LevelSolved.objects.filter(
                    user=user, series=sid, level=lid).exists()
            })
            lid+=1
        sid+=1

    data["player"] = "%s %s" % (user.first_name, user.last_name)

    return HttpResponse(
        json.dumps(data),
        content_type="application/json")


@login_required
def level(request, sid, lid):
    sid = int(sid)
    lid = int(lid)
    data = load_level_index()
    
    try:
        path = data["series"][sid]["levels"][lid]
        task_ids_map = data["series"][sid]["task_ids"]
    except (KeyError, IndexError):
        raise Http404()

    if request.method == 'GET':
        return sendfile(
            request, os.path.join(DATA_ROOT, path), encoding="utf-8")

    if request.method == 'POST':
        user = request.user
        taskpoints = []
        if is_task_rated(task_ids_map["ksp"], user, False):
            taskpoints.append((task_ids_map["ksp"], 2))
        if is_task_rated(task_ids_map["prask"], user, True):
            taskpoints.append((task_ids_map["prask"], 3))
        if len(taskpoints)==0:
            return HttpResponse(status=406)

        if LevelSolved.objects.filter(user=user, series=sid, level=lid).exists():
            return HttpResponse(status=406)

        body = json.loads(request.body)

        submit = LevelSubmit(status="RUN")
        submit.save()

        process_submit.delay(
            user.pk, sid, lid, submit.pk, taskpoints, body['program'], path)

        return HttpResponse(
            json.dumps({"id":submit.pk}),
            content_type="application/json",
            status=202)


def submit_status(request, pk):
    submit = get_object_or_404(LevelSubmit, pk=pk)
    return HttpResponse(
        json.dumps({"status": submit.status}),
        content_type="application/json")


def load_level_index():
    path = os.path.join(DATA_ROOT, "index.json")

    if not os.path.exists(path):
        raise Http404("Level index not found")

    with open(path) as f:
        return json.load(f)


def is_task_rated(task_id, user, prask_only):
    if task_id == 0:
        return False
    if prask_only and user.school_year > 0:
        return False
    return Task.objects.get(pk=task_id).round.can_submit
