from django import template
from ..helpers import make_result_table
from trojsten.regal.tasks.models import Submit

register = template.Library()


@register.inclusion_tag('trojsten/results/parts/results_table.html', takes_context=True)
def show_results_table(context, round, category=None):
    """Displays results for specified tasks and category
    """
    current_tasks, results, has_previous_results = make_result_table(
        context['user'],
        round,
        category,
        single_round=context['single_round'],
        show_staff=context['show_staff'],
        force_generate=context['force_generate'],
    )

    context.update({
        'Submit': Submit,
        'tasks': list(current_tasks),
        'results': results,
        'has_previous_results': has_previous_results
    })
    return context


@register.assignment_tag
def is_frozen(round, single_round=False):
    return round.frozen_results_exists(single_round)
