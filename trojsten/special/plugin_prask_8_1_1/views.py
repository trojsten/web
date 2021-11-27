import json
import os
import subprocess

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import render

from .mark_level_solved import mark_level_solved
from .models import UserLevel

FILE_DIR = os.path.dirname(__file__)
LEVELS_ROOT = os.path.join(FILE_DIR, "levels")


@login_required()
def index(request):
    return render(
        request,
        "plugin_prask_8_1_1/index.html",
    )


@login_required()
def levels(request):
    user = request.user
    data = load_level_index()

    sid = 0
    for serie in data["series"]:
        # Set whether serie is rated
        serie["rated"] = is_serie_rated(serie)
        # Set headers for all levels
        level_paths = serie["levels"]
        serie["levels"] = []
        lid = 0
        for path in level_paths:
            with open(os.path.join(LEVELS_ROOT, path)) as f:
                level = json.load(f)
            serie["levels"].append(
                {
                    "id": "s%dl%d" % (sid, lid),
                    "name": level["name"],
                    "description": level["briefing"],
                    "solved": UserLevel.objects.filter(user=user, series=sid, level=lid).exists(),
                }
            )
            lid += 1
        sid += 1

    data["player"] = "%s %s" % (user.first_name, user.last_name)

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def level(request, sid, lid):
    sid = int(sid)
    lid = int(lid)
    task_id = 0
    ppl = 0

    data = load_level_index()
    level_data = None

    try:
        path = data["series"][sid]["levels"][lid]
        task_id = int(data["series"][sid]["task_id"])
        ppl = int(data["series"][sid]["points_per_level"])
        with open(os.path.join(LEVELS_ROOT, path)) as f:
            level_data = f.read()
    except (KeyError, IndexError):
        raise Http404("Neznamy level.")

    if request.method == "GET":
        return HttpResponse(level_data, content_type="application/json")

    if request.method == "POST":
        user = request.user

        if not is_serie_rated(data["series"][sid]):
            return HttpResponse(
                json.dumps({"type": "UNRATED"}), content_type="application/json", status=200
            )

        if UserLevel.objects.filter(user=user, series=sid, level=lid).exists():
            return HttpResponse(
                json.dumps({"type": "SOLVED"}), content_type="application/json", status=200
            )

        result = run_interpreter(
            user, sid, lid, json.loads(request.body)["programRaw"], json.loads(level_data)
        )
        if result == 1:
            mark_level_solved(task_id, request.user, sid, lid, ppl)

        return HttpResponse(
            json.dumps({"type": "TESTED", "result": result}),
            content_type="application/json",
            status=200,
        )


@login_required
def solution(request, sid, lid):
    sid = int(sid)
    lid = int(lid)
    data = load_level_index()
    solution_data = None

    try:
        path = data["series"][sid]["solutions"][lid]

        with open(os.path.join(LEVELS_ROOT, path)) as f:
            solution_data = f.read()
    except (KeyError, IndexError):
        raise Http404("Neznamy level.")

    return HttpResponse(solution_data, content_type="application/json", status=200)


def load_level_index():
    path = os.path.join(LEVELS_ROOT, "index.json")

    if not os.path.exists(path):
        raise Http404("Level index not found")

    with open(path) as f:
        return json.load(f)


def is_serie_rated(serie):
    if serie["task_id"] == 0:
        return False
    else:
        return True


# Returns 1 if `programRaw` solves `level_data` and 0 otherwise.
def run_interpreter(user, sid, lid, programRaw, level_data):
    try:
        completion = subprocess.run(
            ["node", "--experimental-modules", os.path.join(FILE_DIR, "checker.mjs")],
            input=json.dumps({"programRaw": programRaw, "level": level_data}),
            text=True,
            timeout=1,
        )

        if completion.returncode == 0:
            return 1
        else:
            return 0
    except Exception:
        return 0
