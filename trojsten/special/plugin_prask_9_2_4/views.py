import json
import time
import sys

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from .core import LEVELS, generateResponse, correct
from .models import UserLevel
from .update_points import update_points


@login_required()
def main(request, level=1):
    level = max(min(int(level), 10), 1)
    user = request.user
    userlevel, _ = UserLevel.objects.get_or_create(level=level, user=user)
    
    levels = [[i, False] for i in range(1, len(LEVELS)+1)]
    for x in UserLevel.objects.filter(user=user):
        try:
            levels[x.level - 1][1] = x.solved
        except:
            continue

    return render(
        request,
        "plugin_prask_9_2_4/level.html",
        {
            "level": LEVELS[level - 1],
            "levels": levels,
            "solved": userlevel.solved,
        },
    )

@login_required()
def run(request, level):
    level = max(min(int(level), 10), 1)
    print('run')
    try:
        data = json.loads(request.read().decode("utf-8"))
        userLevel = UserLevel.objects.get(level=level, user=request.user)
    except (KeyError, ValueError):
        return HttpResponseBadRequest()

    text = generateResponse(data['input'], level)
    refresh = False

    if LEVELS[level-1]['type'] == 'answer':
        if correct(text, userLevel):
            update_points(request.user)
            refresh = True

    return HttpResponse(json.dumps({
        'text': text,
        'refresh': refresh,
        'userLevel': LEVELS[userLevel.level]
    }))