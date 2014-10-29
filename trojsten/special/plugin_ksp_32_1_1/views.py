import json

from django.shortcuts import render
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseBadRequest, HttpResponse

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
    for x in userlevel.try_set.order_by('id'):
        try_set.append((x.input, x.output, x.output == target))

    levels = [[i, False] for i in range(1, 11)]
    for x in UserLevel.objects.filter(user=user):
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

    return render(request, 'plugin_ksp_32_1_1/result.json', {
        "level": level,
        "input": _input,
        "output": str(_output),
        "solved": solved,
        "refresh": solved_right_now,
        "try_count": userlevel.try_count,
    }, context_instance=RequestContext(request))


@staff_member_required
def update_all_points(request):
    user_ids = UserLevel.objects.all().values_list('user', flat=True).distinct()
    users = settings.AUTH_USER_MODEL.objects.filter(id__in=user_ids)
    for user in users:
        update_points(user)
    return HttpResponse()
