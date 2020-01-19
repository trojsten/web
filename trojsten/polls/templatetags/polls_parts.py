from django import template

from trojsten.utils import utils

# from trojsten.utils.utils import progress_time, progress_time_precision

register = template.Library()


@register.inclusion_tag("trojsten/polls/parts/progress.html", takes_context=True)
def show_time(context, current_question):
    start = current_question.created_date
    end = current_question.deadline
    data = utils.get_progressbar_data(start, end)
    context.update({"current": current_question, **data})
    return context


@register.filter
def progress_time(delta):
    return utils.progress_time(delta)


@register.filter
def progress_time_precision(delta):
    return utils.progress_time_precision(delta)
