from django.shortcuts import render
from .helpers import get_tasks, check_round_series
from trojsten.regal.tasks.models import Category
from trojsten.regal.contests.models import Round
from django.http import HttpResponseBadRequest


def view_results(request, round_ids, category_ids=None):
    '''Displays results for specified round_ids and category_ids
    '''
    rounds = Round.visible_rounds(request.user).filter(
        pk__in=round_ids.split(',')
    ).select_related('series')
    if len(rounds) == 0 or not check_round_series(rounds):
        return HttpResponseBadRequest()
    categories = None if category_ids is None else Category.objects.filter(
        pk__in=category_ids.split(',')
    )
    tasks = get_tasks(round_ids, category_ids)

    template_data = {
        'rounds': rounds,
        'series': rounds[0].series,
        'categories': categories,
        'tasks': tasks,
        'show_staff': request.GET.get('show_staff', False),
    }
    return render(
        request, 'trojsten/results/view_results.html', template_data
    )


def view_latest_results(request):
    tasks_by_round = {
        r: [
            (cat, get_tasks(
                ','.join(
                    str(round.id)
                    for round in Round.objects.filter(
                        visible=True, series=r.series, number__lte=r.number
                    ).order_by('number')
                ),
                str(getattr(cat, 'id', '')),
            ))
            for cat in [None] + list(Category.objects.filter(competition=c))
        ]
        for c, r in Round.get_latest_by_competition(request.user).items()
    }

    template_data = {
        'tasks_by_round': tasks_by_round,
        'show_staff': request.GET.get('show_staff', False)
    }
    return render(
        request, 'trojsten/results/view_latest_results.html', template_data
    )
