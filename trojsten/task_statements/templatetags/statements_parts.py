# -*- coding: utf-8 -*-

from datetime import datetime

import pytz
from django import template
from django.conf import settings
from django.utils.translation import ungettext as _

from trojsten.results.manager import get_results_tags_for_rounds
from trojsten.submit.models import Submit
from trojsten.tasks.models import Category, Task

from ..helpers import get_points_from_submits, get_rounds_by_year

register = template.Library()


@register.inclusion_tag('trojsten/task_statements/parts/task_list.html', takes_context=True)
def show_task_list(context, round):
    tasks = Task.objects.filter(
        round=round
    ).order_by(
        'number'
    ).select_related(
        'round', 'round__series', 'round__series__competition'
    )
    categories = Category.objects.filter(competition=round.series.competition)

    data = {
        'round': round,
        'tasks': tasks,
        'categories': categories,
        'solutions_visible': round.solutions_are_visible_for_user(context['user']),
    }
    if context['user'].is_authenticated():
        submits = Submit.objects.latest_for_user(tasks, context['user'])
        results = get_points_from_submits(tasks, submits)
        data['points'] = results
    context.update(data)
    return context


@register.inclusion_tag('trojsten/task_statements/parts/buttons.html', takes_context=True)
def show_buttons(context, round):
    (results_tags,) = get_results_tags_for_rounds((round,))

    context.update({
        'round': round,
        'results_tags': results_tags
    })
    return context


@register.inclusion_tag('trojsten/task_statements/parts/round_list.html')
def show_round_list(user, competition):
    all_rounds = get_rounds_by_year(user, competition)
    data = {
        'all_rounds': all_rounds,
    }
    return data


@register.inclusion_tag('trojsten/task_statements/parts/progress.html', takes_context=True)
def show_progress(context, round, results=False):
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
    context.update({
        'round': round,
        'results': results,
        'start': start,
        'end': end,
        'full': full,
        'remaining': remaining,
        'elapsed': elapsed,
        'percent': 100 * elapsed.days // full.days if full.days > 0 else 100,
        'progressbar_class': progressbar_class
    })
    return context


@register.filter
def progress_time(delta):
    if delta.days >= 1:
        count = delta.days
        return _('%(count)d day', '%(count)d days', count) % {'count': count}
    elif delta.seconds // 3600 >= 1:
        count = delta.seconds // 3600
        return _('%(count)d hour', '%(count)d hours', count) % {'count': count}
    elif delta.seconds // 60 >= 1:
        count = delta.seconds // 60
        return _('%(count)d minute', '%(count)d minutes', count) % {'count': count}
    else:
        count = delta.seconds
        return _('%(count)d second', '%(count)d seconds', count) % {'count': count}


@register.filter
def progress_time_precision(delta):
    if delta.days >= 1:
        return 'DAY'
    elif delta.seconds // 3600 >= 1:
        return 'HOUR'
    elif delta.seconds // 60 >= 1:
        return 'MINUTE'
    else:
        return 'SECOND'
