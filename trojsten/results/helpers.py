# -*- coding: utf-8 -*-

from collections import defaultdict, namedtuple


from trojsten.tasks.models import Task, Submit
from trojsten.contests.models import Round
from trojsten.submit import constants as submit_constants
from .models import FrozenResults


class TaskPoints(object):
    def __init__(self):
        self.source_points = 0
        self.description_points = 0
        self.submitted = False
        self.description_pending = False

    @property
    def sum(self):
        return self.description_points + self.source_points

    def add_source_points(self, points):
        self.submitted = True
        self.source_points += points

    def set_description_points(self, points):
        self.submitted = True
        self.description_points = points

    def set_description_pending(self):
        self.submitted = True
        self.description_pending = True
        self.description_points = 0


class FrozenTaskPoints(TaskPoints):
    """frozen version of TaskPoints"""
    def __init__(self, description_points=0, source_points=0, sum=0):
        super(FrozenTaskPoints, self).__init__()
        self.submitted = True
        self.description_points = description_points
        self.source_points = source_points
        self._sum = sum

    @property
    def sum(self):
        return self._sum


class UserResult(object):
    def __init__(self):
        self.previous_rounds_points = 0
        self.tasks = defaultdict(TaskPoints)
        self.rank = None
        self.prev_rank = None

    @property
    def sum(self):
        return self.previous_rounds_points + sum(t.sum for t in self.tasks.values())

    def add_task_points(self, task, submit_type, points, submit_status):
        if submit_type == Submit.DESCRIPTION:
            if submit_status == submit_constants.SUBMIT_STATUS_REVIEWED:
                self.tasks[task.id].set_description_points(points)
            else:
                self.tasks[task.id].set_description_pending()
        else:
            self.tasks[task.id].add_source_points(points)

    def set_previous_rounds_points(self, previous_rounds_points):
        self.previous_rounds_points = previous_rounds_points


class FrozenUserResult(UserResult):
    """frozen version of UserResult"""
    def __init__(self, sum=0, previous_rounds_points=0, rank=None, prev_rank=None):
        super(FrozenUserResult, self).__init__()
        self._sum = sum
        self.previous_rounds_points = previous_rounds_points
        self.rank = rank
        self.prev_rank = prev_rank

    @property
    def sum(self):
        return self._sum

    def add_task(self, task, frozen_task_points):
        self.tasks[task.id] = frozen_task_points


class FrozenUser(object):
    def __init__(self, user, full_name, school_year, school):
        self._user = user
        self._full_name = full_name
        self.school_year = school_year
        self.school = school

    def get_full_name(self):
        return self._full_name

    def __getattr__(self, name):
        return getattr(self._user, name)


def get_results_data(submits):
    """Returns results data for each user who has submitted at least one task
    """
    res = defaultdict(UserResult)
    for submit in submits:
        res[submit.user].add_task_points(
            submit.task, submit.submit_type, submit.user_points, submit.testing_status,
        )
    return res


def get_ranks(score_list):
    """
    Get ranks for score_list
    score_list must be sorted
    """
    last_score = None
    last_rank = 1
    for i, score in enumerate(score_list):
        if score != last_score:
            last_rank = i + 1
        yield last_rank


def merge_results_data(results_data, previous_results_data=None):
    """
    Adds previous_rounds_points from previous_results_data to results_data
    Side effect: This function modifies objects (i.e. individual results)
    contained in results_data
    """
    if previous_results_data:
        for user, data in previous_results_data.items():
            if user not in results_data:
                results_data[user] = UserResult()
            results_data[user].set_previous_rounds_points(data.sum)
    return results_data


def format_results_data(results_data, compute_rank=True):
    """Formats results_data as sorted list of rows so it can be easily displayed as results_table
    Appends user and ranks.
    Side effect: This function modifies objects (i.e. individual results)
    contained in results_data
    """
    Result = namedtuple('Result', ['user', 'data'])
    res = [Result(user=user, data=data) for user, data in results_data.items()]

    if compute_rank:
        res.sort(key=lambda x: -x.data.previous_rounds_points)
        for rank, r in zip(get_ranks(res), res):
            r.data.prev_rank = rank

        res.sort(key=lambda x: -x.data.sum)
        for rank, r in zip(get_ranks(res), res):
            r.data.rank = rank
    else:
        res.sort(key=lambda x: x.data.rank)

    return res


def get_frozen_results(round, category=None, single_round=False):
    def create_frozen_user(frozen_result):
        u = FrozenUser(
            frozen_result.original_user,
            frozen_result.fullname,
            frozen_result.school_year,
            frozen_result.school,
        )
        return u

    frozen_results = FrozenResults.objects.filter(
        round=round, category=category, is_single_round=single_round
    ).order_by(
        '-time'
    )[0]

    frozen_user_results = frozen_results.frozenuserresult_set.all().prefetch_related(
        'task_points__task',
    ).select_related(
        'original_user',
        'school',
    ).order_by('rank')

    results = defaultdict(FrozenUserResult)
    for res in frozen_user_results:
        user = create_frozen_user(res)
        results[user] = FrozenUserResult(
            sum=res.sum,
            previous_rounds_points=res.previous_points,
            rank=res.rank,
            prev_rank=res.prev_rank,
        )

        for tp in res.task_points.all():
            results[user].add_task(tp.task, FrozenTaskPoints(
                description_points=tp.description_points,
                source_points=tp.source_points,
                sum=tp.sum,
            ))

    return (results, frozen_results.has_previous_results)


def make_result_table(
    user,
    round,
    category=None,
    single_round=False,
    show_staff=False,
    force_generate=False,
):
    ResultsTable = namedtuple('ResultsTable', ['tasks', 'results_data', 'has_previous_results'])

    if not (user.is_authenticated()
            and user.is_in_group(round.series.competition.organizers_group)):
        show_staff = False

    current_tasks = Task.objects.for_rounds_and_category(
        [round], category
    ).prefetch_related('category')

    if force_generate or not round.frozen_results_exists(single_round):
        current_submits = Submit.objects.for_tasks(current_tasks, include_staff=show_staff)
        current_results_data = get_results_data(current_submits)

        previous_results_data = None
        if not single_round:
            previous_rounds = Round.objects.visible(user, all_sites=True).filter(
                series=round.series, number__lt=round.number
            ).order_by('number')

            if previous_rounds:
                previous_tasks = Task.objects.for_rounds_and_category(
                    previous_rounds, category
                )
                previous_submits = Submit.objects.for_tasks(
                    previous_tasks, include_staff=show_staff
                )
                previous_results_data = get_results_data(previous_submits)

        final_results = format_results_data(
            merge_results_data(current_results_data, previous_results_data),
        )
        has_previous_results = previous_results_data is not None
    else:
        results, has_previous_results = get_frozen_results(round, category, single_round)
        final_results = format_results_data(
            results,
            compute_rank=False,
        )

    return ResultsTable(
        tasks=current_tasks,
        results_data=final_results,
        has_previous_results=has_previous_results,
    )
