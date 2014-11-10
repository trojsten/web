from django import template
from ..helpers import make_result_table
from trojsten.regal.tasks.models import Submit

register = template.Library()


@register.inclusion_tag('trojsten/results/parts/results_table.html', takes_context=True)
def show_results_table(context, rounds, category=None):
    '''Displays results for specified tasks and category
    '''
    current_tasks, results = make_result_table(rounds, category, context['show_staff'])

    context.update({
        'Submit': Submit,
        'tasks': list(current_tasks),
        'results': results,
        'has_previous_results': len(rounds) > 1
    })
    return context
