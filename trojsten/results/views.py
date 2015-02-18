# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404

from trojsten.regal.tasks.models import Category
from trojsten.regal.contests.models import Round


def is_true(value):
    '''Converts GET parameter value to bool
    '''
    return bool(value) and value.lower() not in ('false', '0')


def view_results(request, round_id, category_id=None):
    '''Displays results for specified round_ids and category_id
    '''
    round = get_object_or_404(
        Round.objects.visible(request.user).select_related('series__competition'),
        pk=round_id,
    )
    category = None if category_id is None else get_object_or_404(Category, pk=category_id)

    context = {
        'round': round,
        'series': round.series,
        'category': category,
        'show_staff': is_true(request.GET.get('show_staff', False)),
        'single_round': is_true(request.GET.get('single_round', False)),
        'force_generate': is_true(request.GET.get('force_generate', False)),
    }
    return render(
        request, 'trojsten/results/view_results.html', context
    )


def view_latest_results(request):
    '''Displays results for latest rounds for each competition
    '''
    rounds = Round.objects.latest_visible(
        request.user
    ).select_related('series__competition')

    rounds_info = zip(
        rounds,
        [
            [None] + list(
                Category.objects.filter(competition=round.series.competition)
            ) for round in rounds
        ],
    )

    context = {
        'rounds_info': rounds_info,
        'show_staff': is_true(request.GET.get('show_staff', False)),
        'single_round': is_true(request.GET.get('single_round', False)),
        'force_generate': is_true(request.GET.get('force_generate', False)),
    }
    return render(
        request, 'trojsten/results/view_latest_results.html', context
    )
