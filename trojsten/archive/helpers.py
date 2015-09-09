from collections import defaultdict
from collections import OrderedDict


from trojsten.regal.contests.models import Round


def get_rounds_by_year(user, competition):
    rounds = Round.objects.visible(
        user
    ).filter(
        series__competition=competition
    ).order_by(
        '-series__year', '-series__number', '-number'
    ).select_related(
        'series__year', 'series__competition'
    ).prefetch_related(
        'series__competition__category_set',
    )
    rounds_dict = defaultdict(list)
    for round in rounds:
        rounds_dict[round.series.year].append(round)

    return OrderedDict(sorted(rounds_dict.items(), key=lambda t: t[0], reverse=True))
