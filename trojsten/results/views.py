# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponseBadRequest

from trojsten.regal.tasks.models import Category
from trojsten.regal.contests.models import Round

from .helpers import check_round_series


def view_results(request, round_ids, category_ids=None):
    '''Displays results for specified round_ids and category_ids
    '''
    rounds = Round.visible_rounds(request.user).filter(
        pk__in=round_ids.split(',')
    ).select_related('series')
    if not rounds or not check_round_series(rounds):
        return HttpResponseBadRequest()
    categories = None if category_ids is None else Category.objects.filter(
        pk__in=category_ids.split(',')
    )

    template_data = {
        'rounds': rounds,
        'series': rounds[0].series,
        'categories': categories,
        'show_staff': request.GET.get('show_staff', False),
        'force_generate': request.GET.get('force_generate', False),
    }
    return render(
        request, 'trojsten/results/view_results.html', template_data
    )


def view_latest_results(request):
    rounds_info = {
        r: {
            'all_rounds': list(
                Round.objects.filter(
                    visible=True, series=r.series
                ).order_by('number')
            ),
            'categories': [None] + list(
                Category.objects.filter(competition=c)
            ),
        }
        for c, r in Round.get_latest_by_competition(request.user).items()
    }

    template_data = {
        'rounds_info': rounds_info,
        'show_staff': request.GET.get('show_staff', False),
        'force_generate': request.GET.get('force_generate', False),
    }
    return render(
        request, 'trojsten/results/view_latest_results.html', template_data
    )
