from django import template
from trojsten.regal.tasks.models import Task, Category
from ..helpers import get_result_rounds, get_rounds_by_year

register = template.Library()


@register.inclusion_tag('trojsten/task_statements/parts/task_list.html')
def show_task_list(round_id):
    tasks = Task.objects.filter(round_id=round_id).order_by('number')
    data = {
        'tasks': tasks,
    }
    return data


@register.inclusion_tag('trojsten/task_statements/parts/buttons.html')
def show_buttons(round):
    result_rounds = get_result_rounds(round)
    categories = Category.objects.filter(competition=round.series.competition)
    data = {
        'round': round,
        'result_rounds': result_rounds,
        'categories': categories,
    }
    return data


@register.inclusion_tag('trojsten/task_statements/parts/round_list.html')
def show_round_list(competition):
    all_rounds = get_rounds_by_year(competition)
    data = {
        'all_rounds': all_rounds,
    }
    return data