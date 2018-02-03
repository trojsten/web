from django import template

register = template.Library()


@register.inclusion_tag('trojsten/results/parts/results_table.html', takes_context=True)
def show_results_table(context, scoreboard, show_staff=False):
    """Displays results for specified tasks and category
    """

    context.update({
        'table': scoreboard.serialized_results,
        'show_staff': show_staff
    })
    return context
