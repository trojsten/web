from django import template
from trojsten.submit.forms import SourceSubmitForm, DescriptionSubmitForm
from trojsten.regal.tasks.models import Submit, SubmitType
from trojsten.submit.views import update_submit

register = template.Library()


@register.inclusion_tag('trojsten/submit/parts/submit_form.html')
def show_submit_form(task, redirect):
    '''Renderne submitovaci formular pre dany task'''
    data = {}
    data['task'] = task
    data['redirect_to'] = redirect
    sourceType = SubmitType.objects.get(pk='source')
    descriptionType = SubmitType.objects.get(pk='description')
    data['has_source'] = sourceType in task.task_types.all()
    data['has_description'] = descriptionType in task.task_types.all()
    if data['has_source']:
        data['source_form'] = SourceSubmitForm()
    if data['has_description']:
        data['description_form'] = DescriptionSubmitForm()
    return data


@register.inclusion_tag('trojsten/submit/parts/submit_list.html')
def show_submit_list(task, person):
    '''Renderne zoznam submitov k danej ulohe pre daneho cloveka'''
    data = {}
    data['task'] = task
    sourceType = SubmitType.objects.get(pk='source')
    descriptionType = SubmitType.objects.get(pk='description')
    data['has_source'] = sourceType in task.task_types.all()
    data['has_description'] = descriptionType in task.task_types.all()
    submits = Submit.objects.filter(task=task, person=person)
    data['source'] = submits.filter(
        submit_type=sourceType).order_by('-time')
    data['description'] = submits.filter(
        submit_type=descriptionType).order_by('-time')
    # Update submits which are not updated yet!
    for submit in data['source'].filter(testing_status='in queue'):
        update_submit(submit)
    return data
