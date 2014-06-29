from django.shortcuts import render
from trojsten.regal.tasks.models import Task, Submit
from django.db.models import Max


def _get_tasks(round_ids, category_ids):
    tasks = Task.objects.filter(
        round__in=round_ids.split(',')
    )
    if category_ids is not None:
        tasks = tasks.filter(
            category__in=category_ids.split(',')
        ).distinct()
    return tasks.order_by('round', 'number')


def _get_submits(tasks):
    # hack aby som mal idcka, predpoklada, ze vacsie id pribudlo do DB neskor
    # da sa vyriesit inner joinom, ale to by chcelo SQL pisat
    return Submit.objects.filter(
        pk__in=Submit.objects.filter(
            task__in=tasks,
        ).values(
            'user', 'task', 'submit_type',
        ).annotate(id=Max('id')).values_list('id', flat=True)
    ).select_related('user', 'task')


def _get_results_data(tasks, submits):
    res = dict()
    for submit in submits:
        if submit.user not in res:
            res[submit.user] = {i: {'sum': 0} for i in tasks}
            res[submit.user]['sum'] = 0
        res[submit.user][submit.task][submit.submit_type] = submit.points
        res[submit.user][submit.task]['sum'] += submit.points
        res[submit.user]['sum'] += submit.points
    return res


def _make_result_table(tasks, submits):
    results_data = _get_results_data(tasks, submits)
    res = list()
    for user, points in results_data.items():
        points_sum = points['sum']
        del points['sum']
        res.append({'user': user, 'points': points, 'sum': points_sum})
    return sorted(res, key=lambda x: -x['sum'])


def view_results(request, round_ids, category_ids=None):
    tasks = _get_tasks(round_ids, category_ids)
    submits = _get_submits(tasks)
    results = _make_result_table(tasks, submits)

    template_data = {
        'tasks': tasks,
        'results': results,
    }
    return render(
        request, 'trojsten/results/view_results.html', template_data
    )
