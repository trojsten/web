from django.shortcuts import render
from .helpers import get_tasks, get_submits, get_results_data, make_result_table
from trojsten.regal.tasks.models import Submit, Category
from trojsten.regal.contests.models import Round


def view_results(request, round_ids, category_ids=None):
    '''Displays results for specified round_ids and category_ids
    '''
    rounds = Round.objects.filter(
        pk__in=round_ids.split(',')
    )
    categories = None if category_ids is None else Category.objects.filter(
        pk__in=category_ids.split(',')
    )
    tasks = get_tasks(round_ids, category_ids)
    submits = get_submits(tasks)
    results_data = get_results_data(tasks, submits)
    results = make_result_table(results_data)

    template_data = {
        'Submit': Submit,
        'rounds': rounds,
        'categories': categories,
        'tasks': tasks,
        'results': results,
    }
    return render(
        request, 'trojsten/results/view_results.html', template_data
    )
