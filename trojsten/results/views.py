# -*- coding: utf-8 -*-

from django.http import Http404
from django.shortcuts import get_object_or_404, render

from trojsten.regal.contests.models import Round
from trojsten.regal.tasks.models import Category
from trojsten.utils.utils import is_true

from .constants import DEFAULT_TAG_KEY
from .manager import TagKeyError, get_results, get_results_tags_for_rounds


def view_results(request, round_id, tag_key=DEFAULT_TAG_KEY):
    """Displays results for specified round_ids and category_id
    """
    round = get_object_or_404(
        Round.objects.visible(request.user).select_related('series__competition'),
        pk=round_id,
    )
    single_round = is_true(request.GET.get('single_round', False))

    try:
        table = get_results(tag_key, round, single_round)
    except TagKeyError:
        raise Http404('Invalid result tag: %s' % tag_key)

    context = {
        'table': table,
        'show_staff': is_true(request.GET.get('show_staff', False)),
    }
    return render(
        request, 'trojsten/results/view_results.html', context
    )


def view_latest_results(request):
    """Displays results for latest rounds for each competition
    """
    rounds = Round.objects.latest_visible(
        request.user
    ).select_related('series__competition')

    single_round = is_true(request.GET.get('single_round', False))

    tables = [
        get_results(result_tag.key, round, single_round)
        for round, result_tags in get_results_tags_for_rounds(rounds)
        for result_tag in result_tags
    ]

    context = {
        'tables': tables,
        'show_staff': is_true(request.GET.get('show_staff', False)),
    }
    return render(
        request, 'trojsten/results/view_latest_results.html', context
    )
