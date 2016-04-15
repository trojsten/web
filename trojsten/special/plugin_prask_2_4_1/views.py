from django.shortcuts import render
from django.http.response import JsonResponse


from .tester import process_question, process_answer


def task_view(request):
    return render(request, 'plugin_prask_2_4_1/task_view.html')


def answer_query(request):
    data = dict()
    if request.method != 'POST':
        data['status'] = 'Error'
        data['message'] = 'Invalid method'
        return JsonResponse(data)
    queries = request.session.get('plugin_prask_2_4_1/questions', list())
    a = request.POST.get('a', None)
    b = request.POST.get('b', None)
    if a is None or b is None:
        data['status'] = 'Error'
        data['message'] = 'Invalid parameters'
        return JsonResponse(data)
    process_question(queries, a, b)
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
