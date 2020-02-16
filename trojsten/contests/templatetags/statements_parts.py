# -*- coding: utf-8 -*-

from django import template

from trojsten.contests.models import Category, Task
from trojsten.results.manager import get_results_tags_for_rounds
from trojsten.submit.models import Submit
from trojsten.utils import utils

from ..helpers import get_points_from_submits, slice_tag_list

register = template.Library()


@register.inclusion_tag("trojsten/contests/parts/task_list.html", takes_context=True)
def show_task_list(context, round):
    tasks = (
        Task.objects.filter(round=round)
        .order_by("number")
        .select_related("round", "round__semester", "round__semester__competition")
        .prefetch_related("categories", "categories__competition")
    )
    # Select all categories which are represented by at least one task in displayed round.
    categories = (
        Category.objects.filter(task__in=tasks.values_list("pk", flat=True))
        .distinct()
        .select_related("competition")
    )

    data = {
        "round": round,
        "tasks": tasks,
        "categories": categories,
        "solutions_visible": round.solutions_are_visible_for_user(context["user"]),
    }
    if context["user"].is_authenticated:
        submits = Submit.objects.latest_for_user(tasks, context["user"])
        results = get_points_from_submits(tasks, submits)
        data["points"] = results
    context.update(data)
    return context


@register.inclusion_tag("trojsten/contests/parts/buttons.html", takes_context=True)
def show_buttons(context, round):
    (results_tags_generator,) = get_results_tags_for_rounds((round,))
    sliced_results_tags = slice_tag_list(list(results_tags_generator))

    context.update({"round": round, "results_tags": sliced_results_tags})
    return context


@register.inclusion_tag("trojsten/contests/parts/progress.html", takes_context=True)
def show_progress(context, round, results=False):
    if round.second_phase_running:
        start = round.end_time
        end = round.second_end_time
    else:
        start = round.start_time
        end = round.end_time
    data = utils.get_progressbar_data(start, end)
    context.update({"round": round, "results": results, **data})
    return context
