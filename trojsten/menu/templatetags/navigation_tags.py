import re

from django import template
from django.conf import settings

from ..models import MenuGroup


register = template.Library()


@register.inclusion_tag('menu/navigation.html', takes_context=True)
def navigation(context):
    menu_groups = MenuGroup.objects.filter(site=settings.SITE_ID)
    menu_groups = menu_groups.order_by('position').prefetch_related('items')
    return {
        'menu_groups': menu_groups,
        'request': context.get('request'),
        'SITE': context.get('SITE'),
        'OTHER_SITES': context.get('OTHER_SITES'),
    }


@register.simple_tag(takes_context=True)
def current(context, pattern, return_value='active', **kwargs):
    if not pattern:
        return ''
    matches = re.search(pattern, context.get('request').path)
    return return_value if matches else ''
