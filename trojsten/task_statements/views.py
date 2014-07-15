from django.http import HttpResponse
from .tasks import compile_task_statements


def notify_push(request):
    compile_task_statements.delay()
    return HttpResponse('')
