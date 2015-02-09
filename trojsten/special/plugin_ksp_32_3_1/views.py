# -*- coding: utf-8 -*-

import json
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

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
        serie["rated"] = bool(serie["taskpoints"])
        del serie["taskpoints"]
        # Set headers for all levels
        level_paths = serie["levels"]
        serie["levels"] = []
        lid = 0
        for path in level_paths:
            with open(os.path.join(DATA_ROOT, path)) as f:
                level = json.load(f)
            serie["levels"].append({
                "id": "s%dl%d" % (sid, lid),
                "name": level["name"],
                "description": level["briefing"],
                "solved": is_level_solved(sid, lid, user)
            })
            lid += 1
        sid += 1

    data["player"] = "%s %s" % (user.first_name, user.last_name)

    return HttpResponse(
        json.dumps(data),
        content_type="application/json")


@login_required
def level(request, sid, lid):
    sid = int(sid)
    lid = int(lid)
    data = load_level_index()
    user = request.user

    try:
        path = data["series"][sid]["levels"][lid]
        taskpoints = data["series"][sid]["taskpoints"]
    except (KeyError, IndexError):
        raise Http404()

    if request.method == 'GET':
        path = os.path.join(DATA_ROOT, path)

        if not os.path.exists(path):
            raise Http404()

        with open(path) as f:
            level_data = json.load(f)

        level_data['rated'] = bool(taskpoints)
        level_data['solved'] = is_level_solved(sid, lid, user)

        return HttpResponse(
            json.dumps(level_data),
            content_type="application/json")

    if request.method == 'POST':
        if is_level_solved(sid, lid, user):
            return HttpResponse(status=406)

        body = json.loads(request.body)

        level_submit = LevelSubmit(status="RUN")
        level_submit.save()

        process_submit.delay(
            user.pk, sid, lid, level_submit.pk,
            taskpoints, body['program'], path)

        return HttpResponse(
            json.dumps({"id": level_submit.pk}),
            content_type="application/json",
            status=202)


@login_required
def solution(request, sid, lid):
    sid = int(sid)
    lid = int(lid)
    data = load_level_index()

    try:
        path = data["series"][sid]["solutions"][lid]
        rated = bool(data["series"][sid]["taskpoints"])
    except (KeyError, IndexError):
        raise Http404()

    if rated or not is_level_solved(sid, lid, request.user):
        raise Http404()

    return sendfile(
        request, os.path.join(DATA_ROOT, path), encoding="utf-8")


@login_required
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


def is_level_solved(sid, lid, user):
    return LevelSolved.objects.filter(
        user=user, series=sid, level=lid).exists()
