from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view

from trojsten.contests.models import Competition
from trojsten.utils.utils import is_true


@api_view(['POST'])
def switch_contest_participation(request):
    user = request.user
    try:
        competition = get_object_or_404(Competition, pk=int(request.POST.get('competition', None)))
    except (TypeError, ValueError):
        return HttpResponseBadRequest()
    ignored = is_true(request.POST.get('value', 'false'))

    if ignored:
        user.ignored_competitions.add(competition)
    else:
        user.ignored_competitions.remove(competition)

    return HttpResponse(status=204)
