from django import template
from trojsten.regal.tasks.models import Task
# from trojsten.regal.contests.models import Round

register = template.Library()


@register.inclusion_tag('trojsten/task_statements/parts/task_list.html')
def show_task_list(round_id):
    tasks = Task.objects.filter(round_id=round_id).order_by('number')
    data = {
        'tasks': tasks,
    }
    return data
