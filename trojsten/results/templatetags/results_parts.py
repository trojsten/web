from django import template
from ..helpers import make_result_table
from trojsten.regal.tasks.models import Submit

register = template.Library()


@register.inclusion_tag('trojsten/results/parts/results_table.html', takes_context=True)
def show_results_table(context, rounds, categories=None):
    '''Displays results for specified tasks and categories
    '''
    current_tasks, results, has_previous_results = make_result_table(rounds, categories, context['show_staff'])

    context.update({
        'Submit': Submit,
        'tasks': list(current_tasks),
        'results': results,
        'has_previous_results': has_previous_results
    })
    return context
