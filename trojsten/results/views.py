from django.shortcuts import render
from trojsten.regal.tasks.models import Task, Submit
from django.db.models import Max


def _get_tasks(round_ids):
    return Task.objects.filter(
        round__in=round_ids.split(',')
    ).order_by('round', 'number')


def _get_submits(tasks):
    # hack aby som mal idcka, predpoklada, ze vacsie id pribudlo do DB neskor
    # da sa vyriesit inner joinom, ale to by chcelo SQL pisat
    return Submit.objects.filter(
        pk__in=Submit.objects.filter(
            task__in=tasks,
        ).values(
            'person', 'task', 'submit_type',
        ).annotate(id=Max('id')).values_list('id', flat=True)
    ).select_related('person', 'task')


def _get_results_data(tasks, submits):
    res = dict()
    for submit in submits:
        if submit.person not in res:
            res[submit.person] = {i: {'sum': 0} for i in tasks}
            res[submit.person]['sum'] = 0
        res[submit.person][submit.task][submit.submit_type] = submit.points
        res[submit.person][submit.task]['sum'] += submit.points
        res[submit.person]['sum'] += submit.points
    return res


def _make_result_table(tasks, submits):
    results_data = _get_results_data(tasks, submits)
    res = list()
    for person, points in results_data.items():
        points_sum = points['sum']
        del points['sum']
        res.append({'person': person, 'points': points, 'sum': points_sum})
    return sorted(res, key=lambda x: -x['sum'])


def view_results(request, round_ids):
    tasks = _get_tasks(round_ids)
    submits = _get_submits(tasks)
    results = _make_result_table(tasks, submits)

    template_data = {
        'tasks': tasks,
        'results': results,
    }
    return render(
        request, 'trojsten/results/view_results.html', template_data
    )
