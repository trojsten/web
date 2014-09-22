from django import template
from django.conf import settings
from trojsten.regal.tasks.models import Task, Category
from ..helpers import get_result_rounds, get_rounds_by_year, get_submits, get_results_data
from datetime import datetime
import pytz


register = template.Library()


@register.inclusion_tag('trojsten/task_statements/parts/task_list.html')
def show_task_list(user, round):
    def prepend_none(iterable):
        yield None
        for i in iterable:
            yield i

    tasks = Task.objects.filter(
        round=round
    ).order_by(
        'number'
    ).select_related(
        'round', 'round__series', 'round__series__competition'
    )
    categories = Category.objects.filter(competition=round.series.competition)

    data = {
        'user': user,
        'round': round,
        'tasks': tasks,
        'categories':  prepend_none(categories),
        'categories_cnt':  categories.count(),
    }
    if user.is_authenticated:
        submits = get_submits(tasks, user)
        results = get_results_data(tasks, submits)
        data['points'] = results
    return data


@register.inclusion_tag('trojsten/task_statements/parts/buttons.html')
def show_buttons(round):
    result_rounds = get_result_rounds(round)
    categories = Category.objects.filter(
        competition=round.series.competition
    ).select_related(
        'competition'
    )
    data = {
        'round': round,
        'result_rounds': result_rounds,
        'categories': categories,
    }
    return data


@register.inclusion_tag('trojsten/task_statements/parts/round_list.html')
def show_round_list(user, competition):
    all_rounds = get_rounds_by_year(user, competition)
    data = {
        'all_rounds': all_rounds,
    }
    return data


@register.inclusion_tag('trojsten/task_statements/parts/progress.html')
def show_progress(round):
    start = round.start_time
    end = round.end_time
    full = end - start
    remaining = end - datetime.now(pytz.utc)
    elapsed = full - remaining
    if remaining.days <= settings.ROUND_PROGRESS_DANGER_DAYS:
        progressbar_class = settings.ROUND_PROGRESS_DANGER_CLASS
    elif remaining.days <= settings.ROUND_PROGRESS_WARNING_DAYS:
        progressbar_class = settings.ROUND_PROGRESS_WARNING_CLASS
    else:
        progressbar_class = settings.ROUND_PROGRESS_DEFAULT_CLASS
    data = {
        'start': start,
        'end': end,
        'full': full,
        'remaining': remaining,
        'elapsed': elapsed,
        'percent': 100 * elapsed.days // full.days,
        'progressbar_class': progressbar_class

    }
    return data
