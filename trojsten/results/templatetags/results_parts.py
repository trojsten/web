from django import template
from ..helpers import get_submits, get_results_data, make_result_table
from trojsten.regal.tasks.models import Submit

register = template.Library()


@register.inclusion_tag('trojsten/results/parts/results_table.html')
def show_results_table(tasks):
    '''Displays results for specified tasks and categories
    '''
    submits = get_submits(tasks)
    results_data = get_results_data(tasks, submits)
    results = make_result_table(results_data)

    data = {
        'Submit': Submit,
        'tasks': tasks,
        'results': results,
    }
    return data
