from django import template

from trojsten.utils import utils

register = template.Library()


@register.inclusion_tag("trojsten/polls/parts/progress.html", takes_context=True)
def show_time(context, current_question):
    start = current_question.created_date
    end = current_question.deadline
    data = utils.get_progressbar_data(start, end)
    context.update({"current": current_question, **data})
    return context
