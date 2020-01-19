import json
from datetime import time
from decimal import Decimal

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import ngettext


def get_progressbar_data(start, end):
    full = end - start
    remaining = end - timezone.now()
    elapsed = full - remaining
    percent = 100 * elapsed.days // full.days if full.days > 0 else 100
    if remaining.days <= settings.ROUND_PROGRESS_DANGER_DAYS:
        progressbar_class = settings.ROUND_PROGRESS_DANGER_CLASS
    elif remaining.days <= settings.ROUND_PROGRESS_WARNING_DAYS:
        progressbar_class = settings.ROUND_PROGRESS_WARNING_CLASS
    else:
        progressbar_class = settings.ROUND_PROGRESS_DEFAULT_CLASS
    return {
        "start": start,
        "end": end,
        "full": full,
        "remaining": remaining,
        "elapsed": elapsed,
        "percent": percent,
        "progressbar_class": progressbar_class,
    }


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


def progress_time_precision(delta):
    if delta.days >= 1:
        return "DAY"
    elif delta.seconds // 3600 >= 1:
        return "HOUR"
    elif delta.seconds // 60 >= 1:
        return "MINUTE"
    else:
        return "SECOND"


def is_true(value):
    """Converts GET parameter value to bool
    """
    return bool(value) and value.lower() not in ("false", "0")


def default_start_time():
    today = timezone.now().date()
    return timezone.make_aware(
        timezone.datetime.combine(today, time.min), timezone.get_current_timezone()
    )


def default_end_time():
    today = timezone.now().date()
    return timezone.make_aware(
        timezone.datetime.combine(today, time.max), timezone.get_current_timezone()
    )


def get_related(attribute_chain, description="", order=None, boolean=False):
    """
    Creates a member function for ModelAdmin.
    This function creates a column of table in admin list view
    when included in list_display.
    However, this can also display attributes of related models.
    list_select_related = True is recommended for ModelAdmin

    Example of getting related "task name" for "submit" model:
    get_task_name = get_related(attribute_chain=('task', 'name'),
                                description='uloha',
                                order='task__name')
    list_display = (get_task_name, )
    """

    def get_attribute_of_related_model(self, obj):
        result = obj
        for attr in attribute_chain:
            result = getattr(result, attr)
        return result() if callable(result) else result

    get_attribute_of_related_model.short_description = description
    get_attribute_of_related_model.admin_order_field = order
    get_attribute_of_related_model.boolean = boolean
    return get_attribute_of_related_model


def attribute_format(attribute, description="", order=None, boolean=False):
    """
    Creates a function for ModelAdmin
    to change format of column in admin list view.
    This function can be used only to reformat a direct attribute of model.
    """
    return get_related((attribute,), description, order, boolean)


def json_response(func):
    """
    A decorator thats takes a view response and turns it
    into json. If a callback is added through GET or POST
    the response is JSONP.
    """

    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        if isinstance(objects, HttpResponse):
            return objects
        try:
            data = json.dumps(objects)
            if "callback" in request.GET:
                # a jsonp response!
                data = "%s(%s);" % (request.GET["callback"], data)
                return HttpResponse(data, "text/javascript")
            if "callback" in request.POST:
                # a jsonp response!
                data = "%s(%s);" % (request.POST["callback"], data)
                return HttpResponse(data, "text/javascript")
        except:  # noqa: E722 @FIXME
            data = json.dumps(str(objects))
        return HttpResponse(data, "application/json")

    return decorator


class Serializable(object):
    def serialize(self):
        return self.serialize_recursive(self.encode())

    def serialize_recursive(self, obj):
        if isinstance(obj, Serializable):
            return obj.serialize()
        elif isinstance(obj, list):
            return [self.serialize_recursive(i) for i in obj]
        elif isinstance(obj, tuple):
            return tuple(self.serialize_recursive(i) for i in obj)
        elif isinstance(obj, dict):
            return {
                self.serialize_recursive(k): self.serialize_recursive(v) for k, v in obj.items()
            }
        elif isinstance(obj, Decimal):
            return str(obj)
        else:
            return obj

    def encode(self):
        return self.__dict__
