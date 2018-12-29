import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

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

    target = LEVELS[level].TARGET

    try_set = []
    for x in userlevel.try_set.order_by('id'):
        try_set.append((x.input, x.output, x.output == target))

    levels = [[i + 1, False] for i in range(MAX_LEVELS)]
    for x in UserLevel.objects.filter(user=user):
        levels[x.level_id - 1][1] = x.solved

    return render(request, 'plugin_prask_5_2_1/level.html', {
        "level": level,
        "levels": levels,
        "solved": userlevel.solved,
        "target": target,
        "try_set": try_set,
        "try_count": userlevel.try_count,
        "try_count_ending":
        {1: '', 2: 'y', 3: 'y', 4: 'y'}.get(userlevel.try_count, 'ov'),
        "maximum": LEVELS[level].MAXIMUM if hasattr(LEVELS[level], 'MAXIMUM') else DEFAULT_MAXIMUM,
    })


@login_required()
def run(request, level=1):
    MAX_INPUT = 10 ** 10 - 1

    level = max(min(int(level), MAX_LEVELS), 1)
    user = request.user
    userlevel, _ = UserLevel.objects.get_or_create(level_id=level, user=user)

    try:
        data = json.loads(request.read().decode("utf-8"))
        _input = int(data["input"])
    except (KeyError, ValueError):
        return HttpResponseBadRequest()

    if _input < 0 or _input > MAX_INPUT:
        return HttpResponseBadRequest()

    _output = LEVELS[level].run(_input, userlevel.try_count)

    solved = _output == LEVELS[level].TARGET
    solved_right_now = solved and not userlevel.solved

    if not userlevel.solved:
        assert isinstance(_output, object)
        userlevel.add_try(str(_input), _output)

    if solved_right_now:
        userlevel.solved = True
        userlevel.save()
        update_points(user)

    return HttpResponse(
        json.dumps({
            "level": level,
            "input": str(_input),
            "output": _output,
            "solved": solved,
            "refresh": solved_right_now,
            "try_count": userlevel.try_count,
            "next_url": reverse('plugin_zwarte:run', args=(level,),
                                current_app=request.resolver_match.namespace)
        }),
        content_type="application/json",
    )
