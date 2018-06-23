from collections import OrderedDict
from django import template

from trojsten.contests.models import Competition

from ..helpers import get_rounds_by_year, slice_tag_list

register = template.Library()


def slice_tags(round_tag):
    return round_tag[0], slice_tag_list(list(round_tag[1]))


@register.inclusion_tag('trojsten/contests/parts/round_list.html')
def show_round_list(user, competition):
    all_rounds = get_rounds_by_year(user, competition)

    all_rounds = {key: list(map(slice_tags, v)) for key, v in all_rounds.items()}
    all_rounds = OrderedDict(sorted(all_rounds.items(), key=lambda t: t[0], reverse=True))

    data = {
        'all_rounds': all_rounds,
    }
    return data


@register.inclusion_tag('trojsten/contests/parts/archive.html', takes_context=True)
def show_archive(context, active_competition=None):
    competitions = Competition.objects.current_site_only()
    context.update({
        'competitions': competitions,
        'active_competition': active_competition,
    })
    return context
