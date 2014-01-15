from django.shortcuts import render
from trojsten.regal.tasks.models import Task, Submit
from django.db.models import Max


def view_results(request, round_ids):
    res = dict()
    tasks = Task.objects.filter(
        round__in=round_ids.split(',')
    ).order_by('number')

    task_numbers = map(lambda x: x.number, tasks)

    # hack aby som mal idcka, predpoklada, ze vacsie id pribudlo do DB neskor
    # da sa vyriesit inner joinom, ale to by chcelo SQL pisat
    submits = Submit.objects.filter(
        pk__in=Submit.objects.filter(
            task__in=tasks,
        ).values(
            'person', 'task', 'submit_type',
        ).annotate(id=Max('id')).values_list('id', flat=True)
    ).select_related('person', 'task')

    r = dict()
    for submit in submits:
        if submit.person not in r:
            r[submit.person] = {i: {'sum': 0} for i in task_numbers}
            r[submit.person]['sum'] = 0
        r[submit.person][submit.task.number][submit.submit_type]\
            = submit.points
        r[submit.person][submit.task.number]['sum'] += submit.points
        r[submit.person]['sum'] += submit.points

    res = []

    for person, points in r.items():
        points_sum = points['sum']
        del points['sum']
        res.append({'person': person, 'points': points, 'sum': points_sum})

    template_data = {
        'numbers': task_numbers,
        'results': sorted(res, key=lambda x: -x['sum']),
    }
    return render(
        request, 'trojsten/results/view_results.html', template_data
    )
