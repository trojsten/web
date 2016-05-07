from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import UserLevel
from .update_points import update_points


@login_required()
def solved(request, level):
    user = request.user
    userlevel, created = UserLevel.objects.get_or_create(level=level, user=user)

    if created:
        update_points(user)

    backlink = {
        1: 'https://ksp.sk/~prask/specialne/2/4/3/#/f9cbeabf3adf',
        2: 'https://ksp.sk/~prask/specialne/2/4/3/#/50ed1a145675',
        3: 'https://ksp.sk/~prask/specialne/2/4/3/#/03f76fd7d802',
    }.get(level, '#')

    return render(request, 'plugin_prask_2_4_3/level.html', {
        "created": created,
        "backlink": backlink,
    }, current_app=request.resolver_match.namespace)
