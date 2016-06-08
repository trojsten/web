from collections import OrderedDict, defaultdict

from trojsten.contests.models import Round
from trojsten.results.helpers import UserResult
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

    results_tags = get_results_tags_for_rounds(rounds)

    rounds_dict = defaultdict(list)
    for round, result_tags in zip(rounds, results_tags):
        rounds_dict[round.series.year].append((round, result_tags))

    return OrderedDict(sorted(rounds_dict.items(), key=lambda t: t[0], reverse=True))


def get_points_from_submits(tasks, submits):
    """Returns results data for each task
    """
    res = UserResult()
    for submit in submits:
        res.add_task_points(
            submit.task, submit.submit_type, submit.user_points,
            submit.testing_status,
        )
    return res
