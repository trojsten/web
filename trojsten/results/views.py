# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render

from trojsten.contests.models import Competition, Round
from trojsten.utils.utils import is_true

from .constants import DEFAULT_TAG_KEY
from .helpers import get_scoreboards_for_rounds


def view_results(request, round_id, tag_key=DEFAULT_TAG_KEY):
    """Displays results for specified round_ids and category_id"""
    round = get_object_or_404(
        Round.objects.visible(request.user)
        .select_related("semester__competition")
        .prefetch_related("semester__competition__required_user_props"),
        pk=round_id,
    )

    scoreboards = get_scoreboards_for_rounds([round], request)

    context = {
        "round": round,
        "scoreboards": scoreboards,
        "single_round": scoreboards[0].scoreboard.is_single_round,
        "selected_tag": tag_key,
        "show_staff": is_true(request.GET.get("show_staff", False)),
    }
    return render(request, "trojsten/results/view_results.html", context)


def view_latest_results(request):
    """Displays results for latest rounds for each competition"""
    rounds = [
        round
        for competition in Competition.objects.current_site_only()
        for round in competition.rules.get_actual_result_rounds(competition)
        .select_related("semester__competition")
        .prefetch_related("semester__competition__required_user_props")
    ]

    scoreboards = get_scoreboards_for_rounds(rounds, request)

    context = {
        "selected_tag": scoreboards[0].scoreboard.tag if scoreboards else None,
        "scoreboards": scoreboards,
        "show_staff": is_true(request.GET.get("show_staff", False)),
    }
    return render(request, "trojsten/results/view_latest_results.html", context)
