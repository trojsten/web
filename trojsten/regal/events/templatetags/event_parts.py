# -*- coding: utf-8 -*-

from django import template

from ..models import EventType


register = template.Library()


@register.inclusion_tag('trojsten/regal/parts/event_list.html', takes_context=True)
def show_events(context):
    context.update({
        'event_types': EventType.objects.current_site_only().filter(
            is_camp=True
        ).prefetch_related('event_set'),
    })
    return context
