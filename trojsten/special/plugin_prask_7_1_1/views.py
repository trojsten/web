import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

from .models import UserLevel
from .mark_level_solved import mark_level_solved
from .contants import LEVELS

@login_required()
def intro(request):
    return render(
        request,
        "plugin_prask_7_1_1/intro.html",
    )

@login_required()
def level(request, level):
    mark_level_solved(request.user, level)
    return render(
        request,
        f"plugin_prask_7_1_1/level{level}.html",
        {
            "level": level,
        }
    )

@login_required()
def get_hint(request, level):
    level = int(level)
    level = max(min(level, len(LEVELS)), 0)
    userlevel, _ = UserLevel.objects.get_or_create(level_id=level, user=request.user)

    if userlevel.solved is not True:
        userlevel.used_hint = True
        userlevel.save()

    return HttpResponse(
        json.dumps(
            {
                "level": level,
                "hint": LEVELS[level].hint
            }
        ),
        content_type="application/json",
    )