from django import template

from trojsten.regal.tasks.models import Submit

from ..helpers import make_result_table

register = template.Library()


@register.inclusion_tag('trojsten/results/parts/results_table.html', takes_context=True)
def show_results_table(context, table, show_staff=False):
    """Displays results for specified tasks and category
    """

    table.calculate_cell_lists()

    context.update({
        'table': table,
        'show_staff': show_staff
    })
    return context


@register.assignment_tag
def is_frozen(round, single_round=False):
    return round.frozen_results_exists(single_round)
