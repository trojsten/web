import datetime
import json
import logging
import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .constants import LEVELS, LIST_LEVEL_PWD
from .mark_level_solved import mark_level_solved
from .models import UserLevel

logger = logging.getLogger("management_commands")


@login_required()
def intro(request):
    return render(
        request,
        "plugin_prask_7_2_1/intro.html",
    )


def randPermute(str, rand):
    list_str = list(str)
    random.shuffle(list_str, rand)
    return "".join(list_str)


def getListEntries():
    entries = []
    rand = random.seed(0)
    for i in range(1000):
        entries.append(
            {
                "id": i,
                "staci": randPermute("stačí", rand),
                "zadat": randPermute("zadať", rand),
                "hash": randPermute(LIST_LEVEL_PWD, rand),
            }
        )
    entries[845] = {
        "id": 845,
        "staci": "stačí",
        "zadat": "zadať",
        "hash": LIST_LEVEL_PWD,
    }
    return entries


@login_required()
def level(request, level, source_fname):
    mark_level_solved(request.user, level - 1)
    specials = {"cookies": {}, "variables": {}}

    REQUEST_LEVEL_GET_PARAMS = (
        "fbclid=IwAR1enbuNFPHzhrG_9fdjFwGx6HqBPQro0UyD"
        "tGajCo9twqU6MwKwQ7_oUW8&utm_medium=cpc&tar=a3"
        "0d29b63f343d4f326fae63c27c4c224c147aeb87b6a12"
        "6e3dd385858a986ef&password=pokuta&hl=cs&pli=1"
    )
    if source_fname == "request.html" and request.GET.urlencode() != REQUEST_LEVEL_GET_PARAMS:
        return redirect(request.path_info + "?" + REQUEST_LEVEL_GET_PARAMS)

    if source_fname == "heslo.html":
        uname = request.GET.get("username")
        pwd = request.GET.get("password")
        if uname is None or pwd is None:
            return redirect(request.path_info + "?" + "username=&password=")

        if uname == "chad" and pwd == "357159":
            specials["variables"]["feedback"] = "Heslo je legruyere."
        elif uname != "" and pwd != "":
            specials["variables"]["feedback"] = "Zlé meno alebo heslo."

    if source_fname == "list.html":
        page, per_page = request.GET.get("page"), request.GET.get("per_page")
        if page is None or per_page is None:
            return redirect(request.path_info + "?" + "page=1&per_page=5")

        page, per_page = int(page), int(per_page)
        start = (page - 1) * per_page
        end = (page) * per_page
        specials["variables"]["entries"] = getListEntries()[start:end]

    response = render(
        request,
        "plugin_prask_7_2_1/" + source_fname,
        {
            "level": level,
            **specials["variables"],
        },
    )

    # Set cookies
    max_cookie_age = 24 * 60 * 60  # One day
    cookie_expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_cookie_age),
        "%a, %d-%b-%Y %H:%M:%S GMT",
    )
    for key in specials["cookies"]:
        response.set_cookie(
            key,
            specials["cookies"][key],
            max_age=max_cookie_age,
            expires=cookie_expires,
            samesite="lax",
        )
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
        json.dumps({"level": level, "hint": LEVELS[level].hint}),
        content_type="application/json",
    )
