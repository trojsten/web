from trojsten.regal.tasks.models import Task, Submit, Category
from trojsten.regal.people.models import User, School
from django.db.models import F
from django.db.models.query import QuerySet
from django.conf import settings
import os
import json
from django.core import serializers
from decimal import Decimal


def get_tasks(rounds, categories=None):
    '''Returns tasks which belong to specified round_ids and category_ids
    '''
    if rounds is None or rounds == []:
        return Task.objects.none()
    tasks = Task.objects.filter(
        round__in=rounds
    )
    if categories is not None and categories != []:
        tasks = tasks.filter(
            category__in=categories
        ).distinct()
    return tasks.order_by('round', 'number')


def get_submits(tasks, show_staff=False):
    '''Returns submits which belong to specified tasks.
    Only one submit per user, submit type and task is returned.
    '''
    submits = Submit.objects
    if not show_staff and len(tasks):
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
    res = dict()
    empty_submit = {'sum': 0, 'description': 0, 'source': 0, 'submitted': False}
    for submit in submits:
        if submit.user not in res:
            res[submit.user] = {task.id: empty_submit.copy() for task in tasks}
            res[submit.user]['sum'] = 0
        if submit.submit_type == Submit.DESCRIPTION:
            res[submit.user][submit.task.id]['description'] = '??'  # Fixme
        else:
            res[submit.user][submit.task.id]['source'] += submit.user_points
        res[submit.user][submit.task.id]['sum'] += submit.user_points
        res[submit.user][submit.task.id]['submitted'] = True
        res[submit.user]['sum'] += submit.user_points
    return res


def format_results_data(results_data, previous_results_data=None):
    '''Makes list of table rows from results_data
    '''
    res = list()
    if previous_results_data is not None:
        for user, points in previous_results_data.items():
            if user not in results_data:
                results_data[user] = dict()
            results_data[user]['previous'] = points['sum']
    for user, points in results_data.items():
        previous_points = points.get('previous', 0)
        points_sum = points.get('sum', 0) + previous_points
        if 'sum' in points:
            del points['sum']
        if 'previous' in points:
            del points['previous']
        res.append({
            'user': user,
            'points': points,
            'sum': points_sum,
            'previous_points': previous_points,
            'show_previous': previous_results_data is not None,
        })

    res = sorted(res, key=lambda x: -x['previous_points'])
    last_points = None
    last_rank = 0
    for i, r in enumerate(res):
        if previous_results_data is not None and r['user'] in previous_results_data:
            if r['previous_points'] != last_points:
                last_rank = i
                r['prev_rank'] = 1 + i
            else:
                r['prev_rank'] = 1 + last_rank
            last_points = r['previous_points']
        else:
            r['prev_rank'] = None

    res = sorted(res, key=lambda x: -x['sum'])
    last_points = None
    last_rank = 0
    for i, r in enumerate(res):
        if r['sum'] != last_points:
            last_rank = i
            r['show_rank'] = True
            r['rank'] = 1 + i
        else:
            r['show_rank'] = False
            r['rank'] = 1 + last_rank
        last_points = r['sum']
    return res


def check_round_series(rounds):
    return all(r.series == rounds[0].series for r in rounds)


def make_result_table(rounds, categories=False, show_staff=False):
    current_round = list(rounds)[-1]
    current_tasks = get_tasks([current_round], categories)
    current_submits = get_submits(current_tasks, show_staff,)
    current_results_data = get_results_data(current_tasks, current_submits)

    previous_results_data = None
    previous_rounds = list(rounds)[:-1]
    if len(previous_rounds):
        previous_tasks = get_tasks(previous_rounds, categories)
        previous_submits = get_submits(previous_tasks, show_staff,)
        previous_results_data = get_results_data(previous_tasks, previous_submits)

    return (
        current_tasks,
        format_results_data(current_results_data, previous_results_data),
        previous_results_data is not None
    )


def get_frozen_results_path(rounds, categories=None):
    s = '#'.join(str(r.id) for r in rounds)
    if categories is not None:
        s += '-' + '#'.join(str(c.id) for c in categories)
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
