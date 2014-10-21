from django import template
from ..helpers import make_result_table, get_frozen_results_path
from trojsten.regal.tasks.models import Submit
import json
import os

register = template.Library()


@register.inclusion_tag('trojsten/results/parts/results_table.html', takes_context=True)
def show_results_table(context, rounds, categories=None):
    '''Displays results for specified tasks and categories
    '''
    path = get_frozen_results_path(rounds, categories)
    force_generate = (
        ('force_generate' in context) and context['force_generate'] and
        (  # only organizer can force generate results
            context['user'].is_superuser or
            rounds[0].series.competition.organizers_group in context['user'].groups.all()
        )
    )
    if os.path.exists(path) and not force_generate:
        with open(path) as f:
            data = json.load(f)
            current_tasks, results = data['current_tasks'], data['results']
    else:
        current_tasks, results = make_result_table(rounds, categories, context['show_staff'])

    context.update({
        'Submit': Submit,
        'tasks': list(current_tasks),
        'results': results,
        'has_previous_results': len(rounds) > 1
    })
    return context


@register.assignment_tag
def is_final(rounds, categories=None):
    return os.path.exists(get_frozen_results_path(rounds, categories))


@register.assignment_tag(takes_context=True)
def is_organizer(context, competition):
    return (
        context['user'].is_superuser or
        competition.organizers_group in context['user'].groups.all()
    )
