from trojsten.regal.tasks.models import Task, Submit, Category
from trojsten.regal.people.models import User, School
from django.db.models import F
from django.db.models.query import QuerySet
from django.conf import settings
import os
import json
from django.core import serializers
from decimal import Decimal
from collections import defaultdict


class TaskPoints:
    def __init__(self):
        self.sum = 0
        self.source_points = 0
        self.description_points = 0
        self.submitted = False
        self.description_pending = False

    def add_source_points(self, points):
        self.submitted = True
        self.source_points += points
        self.sum += self.source_points

    def set_description_points(self, points):
        self.submitted = True
        self.sum -= self.description_points
        self.description_points = points
        self.sum += self.description_points

    def set_pending_description_points(self):
        self.submitted = True
        self.description_pending = True
        self.description_points = '??'


class UserResult:
    def __init__(self):
        self.sum = 0
        self.previous = 0
        self.has_previous_results = False
        self.tasks = defaultdict(TaskPoints)
        self.rank = None
        self.prev_rank = None

    def add_task_points(self, task, submit_type, points):
        self.sum -= self.tasks[task.id].sum
        if submit_type == Submit.DESCRIPTION:
            self.tasks[task.id].set_pending_description_points()  # Fixme
        else:
            self.tasks[task.id].add_source_points(points)
        self.sum += self.tasks[task.id].sum

    def set_previous(self, previous_points):
        self.has_previous_results = True
        self.sum -= self.previous
        self.previous = previous_points
        self.sum += self.previous


def has_permission(group, user):
    return user.is_superuser or (group in user.groups.all())


def get_tasks(rounds, categories=None):
    '''Returns tasks which belong to specified round_ids and category_ids
    '''
    if not rounds:
        return Task.objects.none()
    tasks = Task.objects.filter(
        round__in=rounds
    )
    if categories:
        tasks = tasks.filter(
            category__in=categories
        ).distinct()
    return tasks.order_by('round', 'number')


def get_submits(tasks, show_staff=False):
    '''Returns submits which belong to specified tasks.
    Only one submit per user, submit type and task is returned.
    '''
    submits = Submit.objects
    if not show_staff and tasks:
        submits = submits.exclude(
            # kolo konci Januar 2014 => exclude 2013, 2012,
            # kolo konci Jun 2014 => exclude 2013, 2012,
            # kolo konci September 2014 => exclude 2014, 2013,
            # kolo konci December 2014 => exclude 2014, 2013,
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
        time__lte=F('task__round__end_time'),
    ).order_by(
        'user', 'task', 'submit_type', '-time', '-id',
    ).distinct(
        'user', 'task', 'submit_type'
    ).prefetch_related('user', 'task')


def get_results_data(tasks, submits):
    '''Returns results data for each user who has submitted at least one task
    '''
    res = defaultdict(UserResult)
    for submit in submits:
        res[submit.user].add_task_points(
            submit.task, submit.submit_type, submit.points
        )
    return res


def get_ranks(score_list):
    last_score = None
    last_rank = 1
    for i, score in enumerate(score_list):
        if score != last_score:
            last_rank = i + 1
        yield last_rank


def format_results_data(results_data, previous_results_data=None):
    '''Makes list of table rows from results_data
    '''
    res = list()
    if previous_results_data:
        for user, data in previous_results_data.items():
            if user not in results_data:
                results_data[user] = UserResult()
            results_data[user].set_previous(data.sum)

    for user, data in results_data.items():
        res.append({
            'user': user,
            'data': data,
        })

    res = sorted(res, key=lambda x: -x['data'].previous)
    for rank, r in zip(get_ranks(res), res):
        r['data'].prev_rank = rank

    res = sorted(res, key=lambda x: -x['data'].sum)
    for rank, r in zip(get_ranks(res), res):
        r['data'].rank = rank

    return res


def check_round_series(rounds):
    return all(r.series == rounds[0].series for r in rounds)


def make_result_table(rounds, categories=None, show_staff=False):
    if not rounds:
        return (list(), list())
    current_round = list(rounds)[-1]
    current_tasks = get_tasks([current_round], categories)
    current_submits = get_submits(current_tasks, show_staff)
    current_results_data = get_results_data(current_tasks, current_submits)

    previous_results_data = None
    previous_rounds = list(rounds)[:-1]
    if previous_rounds:
        previous_tasks = get_tasks(previous_rounds, categories)
        previous_submits = get_submits(previous_tasks, show_staff)
        previous_results_data = get_results_data(previous_tasks, previous_submits)

    return (
        current_tasks,
        format_results_data(current_results_data, previous_results_data),
    )


def get_frozen_results_path(rounds, categories=None):
    s = '#'.join(str(r.id) for r in rounds)
    if categories and [cat for cat in categories if cat]:
        s += '-' + '#'.join(
            str(c.id) for c in (cat for cat in sorted(categories) if cat)
        )
    return os.path.join(
        settings.FROZEN_RESULTS_PATH,
        'results_%s.json' % s
    )


class ResultsEncoder(json.JSONEncoder):
    def encode_user(self, obj):
        return {
            'id': obj.id,
            'username': obj.username,
            'first_name': obj.first_name,
            'last_name': obj.last_name,
            'school_year': obj.school_year,
            'school': obj.school,
        }

    def encode_task(self, obj):
        return {
            'id': obj.id,
            'number': obj.number,
            'name': obj.name,
            'category': list(obj.category.all()),
            'external_submit_link': obj.external_submit_link,
            'has_description': obj.has_description,
            'has_source': obj.has_source,
            'has_testablezip': obj.has_testablezip,
            'integer_source_points': obj.integer_source_points,
            'source_points': obj.source_points,
            'description_points': obj.description_points,
        }

    def encode_school(self, obj):
        return {
            'id': obj.id,
            'abbreviation': obj.abbreviation,
            'verbose_name': obj.verbose_name,
            'has_abbreviation': obj.has_abbreviation,
        }

    def encode_category(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
            'full_name': obj.full_name,
        }

    def default(self, obj):
        if isinstance(obj, QuerySet):
            return serializers.serialize('json', obj)
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, User):
            return self.encode_user(obj)
        if isinstance(obj, School):
            return self.encode_school(obj)
        if isinstance(obj, Task):
            return self.encode_task(obj)
        if isinstance(obj, Category):
            return self.encode_category(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
