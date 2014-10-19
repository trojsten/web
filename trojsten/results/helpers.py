from trojsten.regal.tasks.models import Task, Submit
from trojsten.regal.people.models import User
from django.db.models import F
from django.conf import settings


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
            res[submit.user] = {i: empty_submit.copy() for i in tasks}
            res[submit.user]['sum'] = 0
        if submit.submit_type == Submit.DESCRIPTION:
            res[submit.user][submit.task]['description'] = '??'  # Fixme
        else:
            res[submit.user][submit.task]['source'] += submit.user_points
        res[submit.user][submit.task]['sum'] += submit.user_points
        res[submit.user][submit.task]['submitted'] = True
        res[submit.user]['sum'] += submit.user_points
    return res


def make_result_table(results_data):
    '''Makes list of table rows from results_data
    '''
    res = list()
    for user, points in results_data.items():
        points_sum = points['sum']
        del points['sum']
        res.append({'user': user, 'points': points, 'sum': points_sum})
    return sorted(res, key=lambda x: -x['sum'])


def check_round_series(rounds):
    return all(r.series == rounds[0].series for r in rounds)
