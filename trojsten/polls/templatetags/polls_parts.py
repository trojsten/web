from django import template
from django.conf import settings
from django.utils import timezone

from datetime import datetime
from trojsten.polls.models import Question


register = template.Library()


@register.inclusion_tag("trojsten/polls/parts/progress.html")
def show_time(current_question):
    start = current_question.created_date
    end = current_question.deadline
    full = end - start
    remaining = end - timezone.now()
    elapsed = full - remaining
    if remaining.days <= settings.ROUND_PROGRESS_DANGER_DAYS:
        progressbar_class = settings.ROUND_PROGRESS_DANGER_CLASS
    elif remaining.days <= settings.ROUND_PROGRESS_WARNING_DAYS:
        progressbar_class = settings.ROUND_PROGRESS_WARNING_CLASS
    else:
        progressbar_class = settings.ROUND_PROGRESS_DEFAULT_CLASS
    return {
            "current": current_question,
            "start": start,
            "end": end,
            "full": full,
            "remaining": remaining,
            "elapsed": elapsed,
            "percent": 100 * elapsed.days // full.days if full.days > 0 else 100,
            "progressbar_class": progressbar_class,
        }


def get_type(number):
    if number==1:
        return 0
    elif 2<=number<=4:
        return 1
    else:
        return 2


@register.filter
def progress_time(delta):
    if delta.days >= 1:
        count = delta.days
        return str(count) + " " + ["deň", "dni", "dní"][get_type(count)]
    elif delta.seconds // 3600 >= 1:
        count = delta.seconds // 3600
        return str(count) + " " + ["hodina", "hodiny", "hodín"][get_type(count)]
    elif delta.seconds // 60 >= 1:
        count = delta.seconds // 60
        return str(count) + " " + ["minúta", "minúty", "minút"][get_type(count)]
    else:
        count = delta.seconds
        return str(count) + " " + ["sekunda", "sekundy", "sekúnd"][get_type(count)]


@register.filter
def progress_time_precision(delta):
    if delta.days >= 1:
        return "DAY"
    elif delta.seconds // 3600 >= 1:
        return "HOUR"
    elif delta.seconds // 60 >= 1:
        return "MINUTE"
    else:
        return "SECOND"