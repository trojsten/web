from collections import OrderedDict, defaultdict

from trojsten.regal.contests.models import Round
from trojsten.results.manager import get_results_tags_for_rounds


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

    rounds_with_tags = get_results_tags_for_rounds(rounds)

    rounds_dict = defaultdict(list)
    for round, result_tags in rounds_with_tags:
        rounds_dict[round.series.year].append((round, result_tags))

    return OrderedDict(sorted(rounds_dict.items(), key=lambda t: t[0], reverse=True))
