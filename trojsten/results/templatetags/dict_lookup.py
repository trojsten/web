from django import template

register = template.Library()


@register.filter
def lookup(d, key):
    if key in d:
        return d[key]
