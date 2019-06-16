# -*- coding: utf-8 -*-

import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from django.urls import reverse

from .algorithms import ALL
from .getcat import getcat
from .models import UserCategory, Visit
from .submit import update_points

GRATULATION = "Gratulujeme! Prefíkaný kocúr je tvoj. Stačilo ti %d návštev."

urlky = []


@login_required
def root(request):

    return render(request, "plugin_prask_1_2_1/root.html", {"streets": _streets()})


@login_required()
def main(request, category, number=0):

    number = int(number)
    if 0 > number or number > 1000:
        return HttpResponseNotFound("Dom s takýmto číslom neexistuje.")

    algorithm = ALL[category]

    should_update = False

    with transaction.atomic():
        inst, created = UserCategory.objects.get_or_create(category=category, user=request.user)

        if created:
            state = algorithm.get_initial_state()
        else:
            state = json.loads(inst.state)

        previous = list(inst.visits.order_by("pk"))

        if number > 0 and len(previous) < 100:
            response, state, solved = algorithm.response(number, state, previous)

            if solved:
                if inst.points < response:
                    inst.points = response
                    should_update = True
                response = GRATULATION % (len(previous) + 1)
            else:
                visit = Visit(user_category=inst, number=number, response=response)
                response = algorithm.format(response)
                previous.append(visit)
                visit.save()
        else:
            response = ""

        inst.state = json.dumps(state)
        inst.save()

    if should_update:
        update_points(request.user)

    if len(previous) >= 100:
        return render(
            request,
            "plugin_prask_1_2_1/out.html",
            {"street": algorithm.NAME, "streets": _streets(), "category": category},
        )
    else:
        return render(
            request,
            "plugin_prask_1_2_1/main.html",
            {
                "street": algorithm.NAME,
                "streets": _streets(),
                "category": category,
                "number": number,
                "response": response,
                "previous": reversed(previous),
                "points": inst.points,
                "cat_url": getcat(),
            },
        )


@login_required()
def reset(request, category):

    algorithm = ALL[category]

    with transaction.atomic():
        inst, created = UserCategory.objects.get_or_create(category=category, user=request.user)

        inst.state = json.dumps(algorithm.get_initial_state())
        inst.save()

        inst.visits.all().delete()

    return redirect(reverse("plugin_prask_1_2_1_main", kwargs={"category": category}))


def post(request, category):
    number = request.POST.get("number", 0)

    try:
        number = int(number)
        if number < 0:
            number = 0
        if number > 1000:
            number = 0
    except ValueError:
        number = 0

    return redirect(
        reverse("plugin_prask_1_2_1_visit", kwargs={"category": category, "number": number})
    )


def _streets():
    return [(key, ALL[key].NAME) for key in ["A", "B", "C"]]
