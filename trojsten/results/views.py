# -*- coding: utf-8 -*-
from collections import namedtuple

from django.http import Http404
from django.shortcuts import get_object_or_404, render

from trojsten.contests.models import Competition, Round
from trojsten.utils.utils import is_true

from .constants import DEFAULT_TAG_KEY
from .manager import TagKeyError, get_results, get_results_tags_for_rounds


def view_results(request, round_id, tag_key=DEFAULT_TAG_KEY):
    """Displays results for specified round_ids and category_id
    """
    round = get_object_or_404(
        Round.objects.visible(
            request.user
        ).select_related(
            'semester__competition'
        ).prefetch_related(
            'semester__competition__required_user_props'
        ),
        pk=round_id,
    )
    single_round = is_true(request.GET.get('single_round', False))

    ResultTableObject = namedtuple(
        'ResultTableObject', ['scoreboard', 'tag_name', 'competition_ignored', 'user_valid']
    )

    scoreboards = [
        ResultTableObject(
            get_results(result_tag.key, round, single_round),
            result_tag.name,
            request.user.is_anonymous() or request.user.is_competition_ignored(
                round.semester.competition
            ),
            request.user.is_anonymous() or request.user.is_valid_for_competition(
                round.semester.competition
            ),
        )
        for result_tags in get_results_tags_for_rounds([round])
        for result_tag in result_tags
    ]

    context = {
        'round_score' : scoreboards[0][0],
        'scoreboards': scoreboards,
        'selected_tag' : tag_key,
        'tag_name': round.semester.competition.rules.RESULTS_TAGS.get(tag_key).name,
        'show_staff': is_true(request.GET.get('show_staff', False)),
    }
    return render(
        request, 'trojsten/results/view_results.html', context
    )


def view_latest_results(request):
    """Displays results for latest rounds for each competition
    """
    rounds = [
        round
        for competition in Competition.objects.current_site_only()
        for round in competition.rules.get_actual_result_rounds(
            competition
        ).select_related(
            'semester__competition'
        ).prefetch_related(
            'semester__competition__required_user_props'
        )
    ]

    single_round = is_true(request.GET.get('single_round', False))

    ResultTableObject = namedtuple(
        'ResultTableObject', ['scoreboard', 'tag_name', 'competition_ignored', 'user_valid']
    )

    scoreboards = [
        ResultTableObject(
            get_results(result_tag.key, round, single_round),
            result_tag.name,
            request.user.is_anonymous() or request.user.is_competition_ignored(
                round.semester.competition
            ),
            request.user.is_anonymous() or request.user.is_valid_for_competition(
                round.semester.competition
            ),
        )
        for round, result_tags in zip(rounds, get_results_tags_for_rounds(rounds))
        for result_tag in result_tags
    ]

    context = {
        'scoreboards': scoreboards,
        'show_staff': is_true(request.GET.get('show_staff', False)),
    }
    return render(
        request, 'trojsten/results/view_latest_results.html', context
    )
