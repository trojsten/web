import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

# from .interpreter import
from .models import UserLevel
from .levels import levels
# from .interpreter import unpack_blockly
from .update_points import update_points


@login_required()
def main(request):
    return redirect('/specialne/ksp/41/1/index.html')

@login_required()
def state(request):
    data = UserLevel.objects.filter(user=request.user)
    for level in levels:
        level["solved"] = False
        for d in data:
            if d.level == level["id"]:
                level["solved"] = d.solved
                level["workspace"] = json.loads(d.data)
                break

    return JsonResponse(levels, safe=False)

@login_required()
@csrf_exempt
def save(request):
    data = json.loads(request.body)
    userLevel = UserLevel.objects.get_or_create(user=request.user, level=data["level"])[0]
    userLevel.data = json.dumps(data["data"])
    userLevel.save()

    return JsonResponse({'status': 'ok'})

@login_required()
def run(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests are allowed")

    data = json.loads(request.body)
    level = data["level"]
    # unpack_blockly(data["block"])


    return JsonResponse({})
