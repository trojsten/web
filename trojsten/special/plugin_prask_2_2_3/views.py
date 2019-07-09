from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import UserLink


@login_required()
def get_link(request):
    user = request.user

    if not UserLink.objects.filter(user=user).count():
        selected = UserLink.objects.filter(user=None)[0:1]
        created = UserLink.objects.filter(pk__in=selected).update(user=user)
        if created == 0:
            return render(request, "plugin_prask_2_2_3/nedostatok.html")

    link = UserLink.objects.get(user=user).link
    return redirect(link, permanent=False)
