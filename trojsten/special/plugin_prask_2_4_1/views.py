# coding=utf-8
from __future__ import unicode_literals

from django.shortcuts import render
from django.http.response import JsonResponse

from .tester import process_question, process_answer, POCET_PRVKOV


def task_view(request):
    return render(request, 'plugin_prask_2_4_1/task_view.html')


def answer_query(request):
    data = dict()
    queries = request.session.get('plugin_prask_2_4_1/questions', list())
    if request.method == 'DELETE':
        queries = list()
        request.session['plugin_prask_2_4_1/questions'] = queries
        data['status'] = 'Success'
        data['queries'] = queries
        return JsonResponse(data)
    if request.method == 'GET':
        data['status'] = 'Success'
        data['queries'] = queries
        return JsonResponse(data)
    if request.method != 'POST':
        data['status'] = 'Error'
        data['message'] = 'Invalid method'
        return JsonResponse(data)

    try:
        a = int(request.POST.get('a', None))
        b = int(request.POST.get('b', None))
    except ValueError:
        data['status'] = 'Error'
        data['message'] = 'Musíš zadať celé čísla'
        return JsonResponse(data)

    if a == b:
        data['status'] = 'Error'
        data['message'] = 'Porovnávaš samé so sebou'
        return JsonResponse(data)
    if not (1 <= a <= POCET_PRVKOV and 1 <= b <= POCET_PRVKOV):
        data['status'] = 'Error'
        data['message'] = 'Čísla sú mimo rozsah [%d, %d]' % (1, POCET_PRVKOV)
        return JsonResponse(data)
    if a is None or b is None:
        data['status'] = 'Error'
        data['message'] = 'Nesprávne parametre'
        return JsonResponse(data)
    process_question(queries, a, b)
    request.session['plugin_prask_2_4_1/questions'] = queries
    data['status'] = 'Success'
    data['queries'] = queries
    return JsonResponse(data)


def submit(request):
    data = dict()
    queries = request.session.get('plugin_prask_2_4_1/questions', list())
    if request.method != 'POST':
        data['status'] = 'Error'
        data['message'] = 'Invalid method'
        return JsonResponse(data)
    selection = request.POST.get('selection', None)
    if selection is None:
        data['status'] = 'Error'
        data['message'] = 'Invalid parameters'
        return JsonResponse(data)

    points, message = process_answer(queries, selection)
    data = {
        'status': 'Success',
        'points': points,
        'message': message,
    }
    return JsonResponse(data)
