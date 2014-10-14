from django import template
from ..helpers import get_tasks, get_submits, get_results_data, make_result_table
from trojsten.regal.tasks.models import Submit

register = template.Library()


@register.inclusion_tag('trojsten/results/parts/results_table.html', takes_context=True)
def show_results_table(context, rounds, categories=None):
    '''Displays results for specified tasks and categories
    '''
    current_round = rounds[-1]
    current_tasks = get_tasks([current_round], categories)
    current_submits = get_submits(current_tasks, context['show_staff'],)
    current_results_data = get_results_data(current_tasks, current_submits)

    previous_results_data = None
    previous_rounds = rounds[:-1]
    if len(previous_rounds):
        previous_tasks = get_tasks(previous_rounds, categories)
        previous_submits = get_submits(previous_tasks, context['show_staff'],)
        previous_results_data = get_results_data(previous_tasks, previous_submits)

    results = make_result_table(current_results_data, previous_results_data)

    context.update({
        'Submit': Submit,
        'tasks': current_tasks,
        'results': results,
        'show_previous_results': previous_results_data is not None
    })
    return context
