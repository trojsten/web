from collections import defaultdict

from trojsten.contests.models import Round
from trojsten.results.helpers import UserResult


def get_rounds_by_year(user, competition):
    rounds = Round.objects.visible(
        user
    ).filter(
        series__competition=competition
    ).order_by(
        '-series__year', '-number'
    ).select_related('series__year')
    rounds_dict = defaultdict(list)
    for round in rounds:
        rounds_dict[round.series.year].append(round)
    return dict(rounds_dict)


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
