import json

from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from .core import LEVELS
from .models import UserLevel


@login_required()
def main(request, level=1):
    level = max(min(int(level), 10), 1)
    uid = request.user.id
    userlevel, _ = UserLevel.objects.get_or_create(level_id=level, user_id=uid)

    target = str(LEVELS[level].TARGET)

    try_set = []
    for x in userlevel.try_set.order_by('id'):
        try_set.append((x.input, x.output, x.output == target))

    levels = [[i, False] for i in range(1, 11)]
    for x in UserLevel.objects.filter(user_id=uid):
        levels[x.level_id - 1][1] = x.solved

    return render(request, 'plugin_ksp_32_1_1/level.html', {
        "level": level,
        "levels": levels,
        "solved": userlevel.solved,
        "target": target,
        "try_set": try_set,
        "try_count": userlevel.try_count,
        "try_count_ending":
        {1: '', 2: 'y', 3: 'y', 4: 'y'}.get(userlevel.try_count, 'ov'),
    })


@login_required()
def run(request, level=1):
    level = max(min(int(level), 10), 1)
    uid = request.user.id
    userlevel, _ = UserLevel.objects.get_or_create(level_id=level, user_id=uid)

    data = json.loads(request.read().decode("utf-8"))
    _input = str(int(data["input"]))
    _output = LEVELS[level].run(_input)

    solved = _output == LEVELS[level].TARGET
    solved_right_now = solved and not userlevel.solved

    if not userlevel.solved:
        userlevel.add_try(_input, str(_output))

    if solved_right_now:
        userlevel.solved = True
        userlevel.save()

    return render(request, 'plugin_ksp_32_1_1/result.json', {
        "level": level,
        "input": _input,
        "output": str(_output),
        "solved": solved,
        "refresh": solved_right_now,
        "try_count": userlevel.try_count,
    }, context_instance=RequestContext(request))
