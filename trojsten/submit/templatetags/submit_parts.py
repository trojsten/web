from django import template
from trojsten.submit.forms import SourceSubmitForm, DescriptionSubmitForm
from trojsten.regal.tasks.models import Submit
from trojsten.submit.views import update_submit

register = template.Library()


@register.inclusion_tag('trojsten/submit/parts/submit_form.html')
def show_submit_form(task, redirect):
    '''Renderne submitovaci formular pre dany task'''
    data = {}
    task_types = task.task_type.split(',')
    data['task'] = task
    data['redirect_to'] = redirect
    data['has_source'] = 'source' in task_types
    data['has_description'] = 'description' in task_types
    if data['has_source']:
        data['source_form'] = SourceSubmitForm()
    if data['has_description']:
        data['description_form'] = DescriptionSubmitForm()
    return data


@register.inclusion_tag('trojsten/submit/parts/submit_list.html')
def show_submit_list(task, person, redirect):
    '''Renderne zoznam submitov k danej ulohe pre daneho cloveka'''
    data = {}
    task_types = task.task_type.split(',')
    data['task'] = task
    data['redirect_to'] = redirect
    data['has_source'] = 'source' in task_types
    data['has_description'] = 'description' in task_types
    submits = Submit.objects.filter(task=task, person=person)
    data['source'] = submits.filter(
        submit_type='source').order_by('-time')
    data['description'] = submits.filter(
        submit_type='description').order_by('-time')
    # Update submits which are not updated yet!
    for submit in data['source'].filter(testing_status='in queue'):
        update_submit(submit)
    return data
