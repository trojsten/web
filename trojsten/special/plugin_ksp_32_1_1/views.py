import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

from .core import LEVELS
from .models import UserLevel
from .update_points import update_points


@login_required()
def main(request, level=1):
    level = max(min(int(level), 10), 1)
    user = request.user
    userlevel, _ = UserLevel.objects.get_or_create(level_id=level, user=user)

    target = str(LEVELS[level].TARGET)

    try_set = []
    for x in userlevel.try_set.order_by("id"):
        try_set.append((x.input, x.output, x.output == target))

    levels = [[i, False] for i in range(1, 11)]
    for x in UserLevel.objects.filter(user=user):
        levels[x.level_id - 1][1] = x.solved

    return render(
        request,
        "plugin_ksp_32_1_1/level.html",
        {
            "level": level,
            "levels": levels,
            "solved": userlevel.solved,
            "target": target,
            "try_set": try_set,
            "try_count": userlevel.try_count,
            "try_count_ending": {1: "", 2: "y", 3: "y", 4: "y"}.get(userlevel.try_count, "ov"),
        },
    )


@login_required()
def run(request, level=1):
    level = max(min(int(level), 10), 1)
    user = request.user
    userlevel, _ = UserLevel.objects.get_or_create(level_id=level, user=user)

    try:
        data = json.loads(request.read().decode("utf-8"))
        _input = str(int(data["input"]))
    except (KeyError, ValueError):
        return HttpResponseBadRequest()

    _output = LEVELS[level].run(_input)

    solved = _output == LEVELS[level].TARGET
    solved_right_now = solved and not userlevel.solved

    if not userlevel.solved:
        userlevel.add_try(_input, str(_output))

    if solved_right_now:
        userlevel.solved = True
        userlevel.save()
        update_points(user)

    return HttpResponse(
        json.dumps(
            {
                "level": level,
                "input": str(_input),
                "output": _output,
                "solved": solved,
                "refresh": solved_right_now,
                "try_count": userlevel.try_count,
                "next_url": reverse(
                    "plugin_zwarte:run", args=(level,), current_app=request.resolver_match.namespace
                ),
            }
        ),
        content_type="application/json",
    )
