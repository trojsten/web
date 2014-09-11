from django import template

register = template.Library()


@register.filter
def lookup(d, key):
    if key in d:
        return d[key]


@register.filter
def split(value, arg):
    return value.split(arg)
