from django.shortcuts import render
from trojsten.regal.tasks.models import Task, Submit
from django.db.models import Max, F


def _get_tasks(round_ids, category_ids):
    '''Returns tasks which belong to specified round_ids and category_ids
    '''
    tasks = Task.objects.filter(
        round__in=round_ids.split(',')
    )
    if category_ids is not None:
        tasks = tasks.filter(
            category__in=category_ids.split(',')
        ).distinct()
    return tasks.order_by('round', 'number')


def _get_submits(tasks):
    '''Returns submits which belong to specified tasks.
    Only one submit per user, submit type and task is returned.
    '''
    return Submit.objects.filter(
        pk__in=Submit.objects.filter(
            task__in=tasks,
            submit_time__lte=F('task__round__end_time'),
        ).values(
            'user', 'task', 'submit_type',
        ).annotate(
            last_submit_time=Max('submit_time')
        ).filter(
            submit_time=F('last_submit_time')
        ).values_list('id', flat=True)
    ).select_related('user', 'task')


def _get_results_data(tasks, submits):
    '''Returns results data for each user who has submitted at least one task
    '''
    res = dict()
    for submit in submits:
        if submit.user not in res:
            res[submit.user] = {i: {'sum': 0, 'submitted': False} for i in tasks}
            res[submit.user]['sum'] = 0
        res[submit.user][submit.task][int(submit.submit_type)] = submit.points
        res[submit.user][submit.task]['sum'] += submit.points
        res[submit.user][submit.task]['submitted'] = True
        res[submit.user]['sum'] += submit.points
    return res


def _make_result_table(results_data):
    '''Makes list of table rows from results_data
    '''
    res = list()
    for user, points in results_data.items():
        points_sum = points['sum']
        del points['sum']
        res.append({'user': user, 'points': points, 'sum': points_sum})
    return sorted(res, key=lambda x: -x['sum'])


def view_results(request, round_ids, category_ids=None):
    '''Displays results for specified round_ids and category_ids
    '''
    tasks = _get_tasks(round_ids, category_ids)
    submits = _get_submits(tasks)
    results_data = _get_results_data(tasks, submits)
    results = _make_result_table(results_data)

    template_data = {
        'Submit': Submit,
        'tasks': tasks,
        'results': results,
    }
    return render(
        request, 'trojsten/results/view_results.html', template_data
    )
