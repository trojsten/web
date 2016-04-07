# -*- coding: utf-8 -*-

from django import template


register = template.Library()


@register.inclusion_tag('trojsten/regal/parts/event_list.html', takes_context=True)
def show_events(context):
    return context
