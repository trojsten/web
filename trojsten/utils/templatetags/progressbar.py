from django import template
from django.utils.translation import ngettext

register = template.Library()


@register.filter
def progress_time(delta):
    if delta.days >= 1:
        count = delta.days
        return ngettext("%(count)d day", "%(count)d days", count) % {"count": count}
    elif delta.seconds // 3600 >= 1:
        count = delta.seconds // 3600
        return ngettext("%(count)d hour", "%(count)d hours", count) % {"count": count}
    elif delta.seconds // 60 >= 1:
        count = delta.seconds // 60
        return ngettext("%(count)d minute", "%(count)d minutes", count) % {"count": count}
    else:
        count = delta.seconds
        return ngettext("%(count)d second", "%(count)d seconds", count) % {"count": count}


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
