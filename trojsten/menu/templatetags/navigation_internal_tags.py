from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def item_active_class(context, menu_item, return_value='active'):
    if menu_item.is_active(context.get('request').path):
        return return_value
    else:
        return ''
