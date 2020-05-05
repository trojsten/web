import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

from .core import LEVELS
from .models import UserLevel
from .update_points import update_points

MAX_LEVELS = 10


@login_required()
def main(request, level=1):
    DEFAULT_MAXIMUM = 9999999999

    level = max(min(int(level), MAX_LEVELS), 1)
    user = request.user
    userlevel, _ = UserLevel.objects.get_or_create(level_id=level, user=user)

    examples_match = [[i, 'darkorange'] for i in LEVELS[level].TABLE_MATCH]
    examples_neg = [[i, 'darkorange'] for i in LEVELS[level].TABLE_NEGATIVE]

    try_set = []
    last_input = None

    for x in userlevel.try_set.order_by("id"):
        last_input = x.input
        try_set.append((x.input, x.output, True if x.output == 'True' else False))

    levels = [[i + 1, False] for i in range(MAX_LEVELS)]
    for x in UserLevel.objects.filter(user=user):
        levels[x.level_id - 1][1] = x.solved

    return render(
        request,
        "plugin_prask_5_1_1/level.html",
        {
            "last_input": last_input,
            "level": level,
            "levels": levels,
            "solved": userlevel.solved,
            "try_set": try_set,
            "try_count": userlevel.try_count,
            "try_count_ending": {1: "", 2: "y", 3: "y", 4: "y"}.get(userlevel.try_count, "ov"),
            "examples_match": examples_match,
            "examples_neg": examples_neg,
            "maximum": LEVELS[level].MAXIMUM
            if hasattr(LEVELS[level], "MAXIMUM")
            else DEFAULT_MAXIMUM,
        },
    )


@login_required()
def run(request, level=1):
    MAX_INPUT = 10 ** 10 - 1

    level = max(min(int(level), MAX_LEVELS), 1)
    user = request.user
    userlevel, _ = UserLevel.objects.get_or_create(level_id=level, user=user)

    try:
        data = json.loads(request.read().decode("utf-8"))
        _input = data["input"]
    except (KeyError, ValueError):
        return HttpResponseBadRequest()

    if len(_input) == 0 or len(_input) > MAX_INPUT:
        return HttpResponseBadRequest()

    _output, match, neg = LEVELS[level].run(_input, userlevel.try_count)

    examples_match = [[i, j] for i, j in zip(LEVELS[level].TABLE_MATCH, match)]
    examples_neg = [[i, j] for i, j in zip(LEVELS[level].TABLE_NEGATIVE, neg)]

    solved = _output
    solved_right_now = solved and not userlevel.solved

    if not userlevel.solved:
        # assert isinstance(_output, object)
        userlevel.add_try(str(_input), _output)

    if solved_right_now:
        userlevel.solved = True
        userlevel.save()
        update_points(user)

    last_input = None
    for x in userlevel.try_set.order_by("id"):
        last_input = x.input

    return HttpResponse(
        json.dumps(
            {
                "answer"
                "level": level,
                "input": _input,
                "last_input": last_input,
                "output": "Správne " if _output else "Nesprávne",
                "solved": solved,
                "refresh": solved_right_now,
                "try_count": userlevel.try_count,
                "examples_match": examples_match,
                "examples_neg": examples_neg,
                "next_url": reverse(
                    "plugin_zwarte:run", args=(level,), current_app=request.resolver_match.namespace
                ),
            }
        ),
        content_type="application/json",
    )
