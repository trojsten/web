from django import template

from ..helpers import get_rounds_by_year

register = template.Library()


@register.inclusion_tag('trojsten/archive/parts/round_list.html')
def show_round_list(user, competition):
    all_rounds = get_rounds_by_year(user, competition)
    data = {
        'all_rounds': all_rounds,
    }
    return data
