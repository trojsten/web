# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from .helpers import (check_round_series, make_result_table,
                      get_frozen_results_path, ResultsEncoder, has_permission)
from trojsten.regal.tasks.models import Category
from trojsten.regal.contests.models import Round
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
import json


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
            'all_rounds': [
                round
                for round in Round.objects.filter(
                    visible=True, series=r.series, number__lte=r.number
                ).order_by('number')
            ],
            'categories': [
                cat
                for cat in [None] + list(
                    Category.objects.filter(competition=c)
                )
            ],
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


@login_required
def freeze_results(request, round_ids, category_ids=None):

    rounds = Round.objects.filter(
        pk__in=round_ids.split(',')
    ).select_related('series__competition__organizers_group')
    if rounds or not check_round_series(rounds):
        return HttpResponseBadRequest()

    if not has_permission(
        rounds[0].series.competition.organizers_group, request.user
    ):
        raise PermissionDenied

    categories = None if not category_ids else Category.objects.filter(
        pk__in=category_ids.split(',')
    )

    current_tasks, results = make_result_table(rounds, categories)
    path = get_frozen_results_path(rounds, categories)

    #serialize data
    with open(path, 'w') as f:
        json.dump({
            'current_tasks': list(current_tasks),
            'results': results,
        }, f, cls=ResultsEncoder, sort_keys=True, indent=4, separators=(',', ': '),)

    messages.add_message(
        request,
        messages.SUCCESS,
        "Výsledkovka bola úspešne zmrazená do súboru: %s" % path,
    )
    return redirect(reverse(
        'view_results',
        kwargs={'round_ids': round_ids, 'category_ids': category_ids},
    ))
