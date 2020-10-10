import json
import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings

from .models import UserLevel
from .mark_level_solved import mark_level_solved
from .contants import LEVELS

@login_required()
def intro(request):
    return render(
        request,
        "plugin_prask_7_1_1/intro.html",
    )

def handle_cookie_level(request, level):
    out = {"cookies": {}, "variables": {}}
    if request.COOKIES.get("ukazHeslo") == "true":
        out["variables"]["password"] = "hihihihi"
    else:
        out["cookies"]["ukazHeslo"] = "false"
    return out

@login_required()
def level(request, level, source_fname):
    mark_level_solved(request.user, level)
    specials = {"cookies": {}, "variables": {}}
    if source_fname == "cookie.html":
        specials = handle_cookie_level(request, level)
    response = render(
        request,
        f"plugin_prask_7_1_1/{source_fname}",
        {
            "level": level,
            **specials["variables"],
        },
    )
    # Set cookies
    max_cookie_age = 24 * 60 * 60 # One day
    cookie_expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_cookie_age),
        "%a, %d-%b-%Y %H:%M:%S GMT")
    for key in specials["cookies"]:
        response.set_cookie(
            key, specials["cookies"][key],max_age=max_cookie_age, expires=cookie_expires,
            domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)
    return response

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

@login_required()
def get_button_password(request):
    return HttpResponse(
        json.dumps(
            {
                "password": 'Heslo je: "slamastika"',
            }
        ),
        content_type="application/json",
    )

@login_required()
def get_input_password(request):
    print(request.POST)
    schnitzels = request.POST.get('schnitzels', None)
    if request.method != "POST" or schnitzels is None:
        return HttpResponseBadRequest("Request must contain schnitzels.")

    password = f"Objednali ste si {schnitzels} rezňov."
    if schnitzels == "1000000":
        password += ' Heslo je "abrakadabra".'
    return HttpResponse(
        json.dumps(
            {
                "password": password,
            }
        ),
        content_type="application/json",
    )