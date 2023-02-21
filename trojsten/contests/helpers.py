from collections import OrderedDict, defaultdict

from trojsten.contests.models import Round
from trojsten.results.helpers import UserResult
from trojsten.results.manager import get_results_tags_for_rounds
from trojsten.submit.constants import SUBMIT_TYPE_DESCRIPTION, SUBMIT_TYPE_TEXT
from trojsten.submit.models import Submit

from .constants import DEFAULT_NUMBER_OF_TAGS, MAX_NUMBER_OF_TAGS


def slice_tag_list(tag_list, maximum=MAX_NUMBER_OF_TAGS, default=DEFAULT_NUMBER_OF_TAGS):
    return tag_list[:default] if len(tag_list) > maximum else tag_list[:maximum]


def get_rounds_by_year(user, competition):
    """
    Returns an OrderedDict keyed by year (in descending order),
    where the values are pairs of (round, list of sliced result tags).
    """
    rounds = (
        Round.objects.visible(user)
        .filter(semester__competition=competition)
        .order_by("-semester__year", "-semester__number", "-number")
        .select_related("semester__competition")
        .prefetch_related("semester__competition__category_set")
    )

    results_tags_for_rounds = get_results_tags_for_rounds(rounds)

    rounds_dict = defaultdict(list)
    for round, results_tags in zip(rounds, results_tags_for_rounds):
        rounds_dict[round.semester.year].append((round, slice_tag_list(list(results_tags))))

    return OrderedDict(sorted(rounds_dict.items(), key=lambda t: t[0], reverse=True))


def get_points_from_submits(tasks, submits):
    """Returns results data for each task"""
    res = UserResult()
    for submit in submits:
        res.add_task_points(
            submit.task, submit.submit_type, submit.user_points, submit.testing_status
        )
    return res


def check_description_at_text_submit(user, tasks):
    user_submits = Submit.objects.latest_for_user(tasks, user)
    for task in tasks:
        if (
            task.has_text_submit
            and task.has_description
            and user_submits.filter(task=task, submit_type=SUBMIT_TYPE_TEXT, points__gt=0)
            and not user_submits.filter(task=task, submit_type=SUBMIT_TYPE_DESCRIPTION)
        ):
            return True
    return False
