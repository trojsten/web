from django.shortcuts import render
from .helpers import get_tasks, get_submits, get_results_data, make_result_table
from trojsten.regal.tasks.models import Submit


def view_results(request, round_ids, category_ids=None):
    '''Displays results for specified round_ids and category_ids
    '''
    tasks = get_tasks(round_ids, category_ids)
    submits = get_submits(tasks)
    results_data = get_results_data(tasks, submits)
    results = make_result_table(results_data)

    template_data = {
        'Submit': Submit,
        'tasks': tasks,
        'results': results,
    }
    return render(
        request, 'trojsten/results/view_results.html', template_data
    )
