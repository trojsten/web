import copy
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from .levels import levels, test_program

# from .interpreter import
from .models import UserLevel

# from .interpreter import unpack_blockly
from .update_points import update_points

bonus = {
    "name": "j. najkratšia cesta",
    "points": [1, 1],
    "numInputs": 2,
    "inputs": [[1, 10], [0, -1]],
    "timelimit": 50000000,
    "allowed": [
        "constant",
        "--",
        "+",
        "-",
        "*",
        "^",
        "sign",
        "≥",
        "≤",
        "<",
        ">",
        "min",
        "max",
        "/",
        "%",
    ],
    "zadanie": "z2j.html",
    "id": 29,
}


@login_required()
def main(request):
    return redirect("/specialne/ksp/41/1/index.html")


@login_required()
def state(request):
    data = UserLevel.objects.filter(user=request.user)
    levels2 = copy.deepcopy(levels)
    for d in data:
        if d.level == 28 and d.solved:
            levels2.append(bonus)

    for level in levels2:
        level["solved"] = False
        for d in data:
            if d.level == level["id"]:
                level["solved"] = d.solved
                level["workspace"] = json.loads(d.data)
                break

    return JsonResponse(levels2, safe=False)


all_levels = levels.copy()
all_levels.append(bonus)


@login_required()
@csrf_exempt
def save(request):
    data = json.loads(request.body)
    is_prask = "prask" in request.get_host()
    userLevel = UserLevel.objects.get_or_create(user=request.user, level=data["level"])[
        0
    ]
    userLevel.data = json.dumps(data["data"])
    level = all_levels[data["level"] - 20]
    status = test_program(data["data"], level)
    if status == "OK":
        userLevel.solved = True
        userLevel.save()
        update_points(request.user, is_prask)
    userLevel.save()
    return JsonResponse({"status": status})


@login_required()
def run(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests are allowed")

    data = json.loads(request.body)
    level = data["level"]
    # unpack_blockly(data["block"])

    return JsonResponse({})
