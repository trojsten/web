# -*- coding: utf-8 -*-

from collections import defaultdict, namedtuple

from django.db.models import F, Q
from django.conf import settings

from trojsten.regal.tasks.models import Task, Submit
from trojsten.regal.people.models import User
from trojsten.regal.contests.models import Round
from trojsten.submit import constants as submit_constants


class TaskPoints:
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


class UserResult:
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
            if submit_status == submit_constants.STATUS_REVIEWED:
                self.tasks[task.id].set_description_points(points)
            else:
                self.tasks[task.id].set_description_pending()
        else:
            self.tasks[task.id].add_source_points(points)

    def set_previous_rounds_points(self, previous_rounds_points):
        self.previous_rounds_points = previous_rounds_points


def get_tasks(rounds, category=None):
    '''Returns tasks which belong to specified round_ids and category_ids
    '''
    if not rounds:
        return Task.objects.none()
    tasks = Task.objects.filter(
        round__in=rounds
    )
    if category:
        tasks = tasks.filter(
            category=category
        )
    return tasks.order_by('round', 'number')


def get_submits(tasks, show_staff=False):
    '''Returns submits which belong to specified tasks.
    Only one submit per user, submit type and task is returned.
    '''
    submits = Submit.objects
    if not show_staff and tasks:
        submits = submits.exclude(
            # round ends January 2014 => exclude 2013, 2012,
            # round ends Jun 2014 => exclude 2013, 2012,
            # round ends September 2014 => exclude 2014, 2013,
            # round ends December 2014 => exclude 2014, 2013,
            user__graduation__lt=tasks[0].round.end_time.year + int(
                tasks[0].round.end_time.month > settings.SCHOOL_YEAR_END_MONTH
            )
        ).exclude(
            user__in=User.objects.filter(
                groups=tasks[0].round.series.competition.organizers_group
            )
        )
    return submits.filter(
        task__in=tasks,
    ).filter(
        Q(time__lte=F('task__round__end_time')) | Q(testing_status=Submit.STATUS_REVIEWED)
    ).order_by(
        'user', 'task', 'submit_type', '-time', '-id',
    ).distinct(
        'user', 'task', 'submit_type'
    ).select_related('user__school', 'task')


def get_results_data(tasks, submits):
    '''Returns results data for each user who has submitted at least one task
    '''
    res = defaultdict(UserResult)
    for submit in submits:
        res[submit.user].add_task_points(
            submit.task, submit.submit_type, submit.user_points, submit.testing_status,
        )
    return res


def get_ranks(score_list):
    '''
    Get ranks for score_list
    score_list must be sorted
    '''
    last_score = None
    last_rank = 1
    for i, score in enumerate(score_list):
        if score != last_score:
            last_rank = i + 1
        yield last_rank


def merge_results_data(results_data, previous_results_data=None):
    '''
    Adds previous_rounds_points from previous_results_data to results_data
    Side effect: This function modifies objects (i.e. individual results)
    contained in results_data
    '''
    if previous_results_data:
        for user, data in previous_results_data.items():
            if user not in results_data:
                results_data[user] = UserResult()
            results_data[user].set_previous_rounds_points(data.sum)
    return results_data


def format_results_data(results_data):
    '''Formats results_data as sorted list of rows so it can be easily displayed as results_table
    Appends user and ranks.
    Side effect: This function modifies objects (i.e. individual results)
    contained in results_data
    '''
    Result = namedtuple('Result', ['user', 'data'])
    res = [Result(user=user, data=data) for user, data in results_data.items()]

    res.sort(key=lambda x: -x.data.previous_rounds_points)
    for rank, r in zip(get_ranks(res), res):
        r.data.prev_rank = rank

    res.sort(key=lambda x: -x.data.sum)
    for rank, r in zip(get_ranks(res), res):
        r.data.rank = rank

    return res


def make_result_table(user, round, category=None, single_round=False, show_staff=False):
    ResultsTable = namedtuple('ResultsTable', ['tasks', 'results_data', 'has_previous_results'])

    if not (
        user.is_authenticated()
        or user.is_in_group(round.series.competition.organizers_group)
    ):
        show_staff = False

    current_tasks = get_tasks([round], category)
    current_submits = get_submits(current_tasks, show_staff)
    current_results_data = get_results_data(current_tasks, current_submits)

    previous_results_data = None
    if not single_round:
        previous_rounds = Round.objects.visible(user).filter(
            series=round.series, number__lt=round.number
        ).order_by('number')

        if previous_rounds:
            previous_tasks = get_tasks(previous_rounds, category)
            previous_submits = get_submits(previous_tasks, show_staff)
            previous_results_data = get_results_data(previous_tasks, previous_submits)

    return ResultsTable(
        tasks=current_tasks,
        results_data=format_results_data(
            merge_results_data(current_results_data, previous_results_data),
        ),
        has_previous_results=previous_results_data is not None,
    )
