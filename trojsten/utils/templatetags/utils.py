# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template
from django.conf import settings

from trojsten.contests.models import Competition

register = template.Library()


@register.filter
def lookup(object, key):
    """
    Looks up for key in object.
    Returns None if key is not found.
    """
    try:
        return object[key]
    except (KeyError, IndexError, TypeError):
        return None


@register.assignment_tag
def lookup_as(object, key):
    """
    Looks up for key in object.
    Returns None if key is not found.
    """
    try:
        return object[key]
    except (KeyError, IndexError, TypeError):
        return None


@register.filter
def choice_text(choices, value):
    for v, t in choices:
        if str(v) == str(value):
            return t
    return None


@register.filter
def split(value, arg):
    return value.split(arg)


@register.filter
def as_list(value):
    return [value]


@register.assignment_tag(takes_context=True)
def is_organizer(context, competition):
    return (
        context['user'].is_superuser
        or competition.organizers_group in context['user'].groups.all()
    )


@register.assignment_tag(takes_context=True)
def is_site_organizer(context):
    return any(map(
        lambda competition: is_organizer(context, competition),
        Competition.objects.current_site_only()
    ))


@register.filter
def exclude(object, key):
    res = object.copy()
    try:
        del res[key]
    except KeyError:
        pass
    return res


@register.assignment_tag
def exclude_as(object, key):
    return exclude(object, key)


@register.filter
def provider_name(key):
    try:
        provider_dict = settings.PROVIDER_OVERRIDE_DICT
    except AttributeError:
        provider_dict = dict()
    if key in provider_dict:
        return provider_dict[key]
    else:
        return key.title()


@register.filter
def school_year(school_year):
    is_elementary = False
    if school_year < 1:
        school_year += 9
        is_elementary = True
    return '{}{}'.format(school_year, 'zš' if is_elementary else '')
