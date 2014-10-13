from django import template
from ..helpers import get_tasks, get_submits, get_results_data, make_result_table
from trojsten.regal.tasks.models import Submit

register = template.Library()


@register.inclusion_tag('trojsten/results/parts/results_table.html', takes_context=True)
def show_results_table(context, rounds, categories=None):
    '''Displays results for specified tasks and categories
    '''
    tasks = get_tasks(rounds, categories)
    submits = get_submits(tasks, context['show_staff'],)
    results_data = get_results_data(tasks, submits)
    results = make_result_table(results_data)

    context.update({
        'Submit': Submit,
        'tasks': tasks,
        'results': results,
    })
    return context
