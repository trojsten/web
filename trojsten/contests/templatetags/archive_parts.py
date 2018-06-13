from django import template

from trojsten.contests.models import Competition

from ..helpers import get_rounds_by_year

register = template.Library()


@register.inclusion_tag('trojsten/contests/parts/round_list.html')
def show_round_list(user, competition):
    all_rounds = get_rounds_by_year(user, competition)
    data = {
        'all_rounds': all_rounds,
        'competition': competition,
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
