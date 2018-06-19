# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ungettext as _

from trojsten.contests.helpers import get_points_from_submits, get_rounds_by_year, slice_if_needed
from trojsten.contests.models import Category, Task
from trojsten.results.manager import get_results_tags_for_rounds
from trojsten.submit.models import Submit


register = template.Library()


@register.inclusion_tag('trojsten/contests/parts/task_list.html', takes_context=True)
def show_task_list(context, round):
    tasks = Task.objects.filter(
        round=round
    ).order_by(
        'number'
    ).select_related(
        'round', 'round__semester', 'round__semester__competition'
    )
    # Select all categories which are represented by at least one task in displayed round.
    categories = Category.objects.filter(task__in=tasks.values_list('pk', flat=True)).distinct()

    data = {
        'round': round,
        'tasks': tasks,
        'categories': categories,
        'solutions_visible': round.solutions_are_visible_for_user(context['user']),
    }
    if context['user'].is_authenticated:
        submits = Submit.objects.latest_for_user(tasks, context['user'])
        results = get_points_from_submits(tasks, submits)
        data['points'] = results
    context.update(data)
    return context


@register.inclusion_tag('trojsten/contests/parts/buttons.html', takes_context=True)
def show_buttons(context, round):
    (results_tags,) = get_results_tags_for_rounds((round,))
    results_tags = slice_if_needed(2, 1, list(results_tags))

    context.update({
        'round': round,
        'results_tags': results_tags
    })
    return context


@register.inclusion_tag('trojsten/contests/parts/round_list.html')
def show_round_list(user, competition):
    all_rounds = get_rounds_by_year(user, competition)
    data = {
        'all_rounds': all_rounds,
    }
    return data


@register.inclusion_tag('trojsten/contests/parts/progress.html', takes_context=True)
def show_progress(context, round, results=False):
    if round.second_phase_running:
        start = round.end_time
        end = round.second_end_time
    else:
        start = round.start_time
        end = round.end_time

    full = end - start
    remaining = end - timezone.now()
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
