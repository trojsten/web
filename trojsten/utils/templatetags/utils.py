import re

from django import template
from django.core import urlresolvers

register = template.Library()


@register.filter
def lookup(object, key):
    '''
    Looks up for key in object.
    Returns None if key is not found.
    '''
    try:
        return object[key]
    except (KeyError, IndexError, TypeError):
        return None


@register.filter
def split(value, arg):
    return value.split(arg)


@register.filter
def as_list(value):
    return [value]


@register.simple_tag(takes_context=True)
def current(context, url_name, return_value='active', **kwargs):
    matches = current_url_equals(context, url_name, **kwargs)
    return return_value if matches else ''


def current_url_equals(context, url_name, **kwargs):
    resolved = False
    try:
        resolved = urlresolvers.resolve(context.get('request').path)
    except:
        pass
    matches = resolved and resolved.url_name == url_name
    if matches and kwargs:
        for key in kwargs:
            kwarg = kwargs.get(key)
            resolved_kwarg = resolved.kwargs.get(key)
            if not resolved_kwarg or kwarg != resolved_kwarg:
                return False
    if not matches:
        return re.search(url_name, context.get('request').path)
    return matches


@register.assignment_tag(takes_context=True)
def is_organizer(context, competition):
    return (
        context['user'].is_superuser or
        competition.organizers_group in context['user'].groups.all()
    )
