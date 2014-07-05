from django import template
from trojsten.submit.forms import SourceSubmitForm, DescriptionSubmitForm
from trojsten.regal.tasks.models import Submit
from trojsten.submit.views import update_submit

register = template.Library()


@register.inclusion_tag('trojsten/submit/parts/submit_form.html')
def show_submit_form(task, redirect):
    '''Renders submit form for specified task'''
    data = {}
    data['task'] = task
    data['Submit'] = Submit
    data['redirect_to'] = redirect
    if task.has_source:
        data['source_form'] = SourceSubmitForm()
    if task.has_description:
        data['description_form'] = DescriptionSubmitForm()
    return data


@register.inclusion_tag('trojsten/submit/parts/submit_list.html')
def show_submit_list(task, user):
    '''Renders submit list for specified task and user'''
    data = {}
    data['task'] = task
    data['Submit'] = Submit
    submits = Submit.objects.filter(task=task, user=user)
    data['submits'] = {
        submit_type: submits.filter(submit_type=submit_type).order_by('-time')
        for submit_type, _ in Submit.SUBMIT_TYPES
    }

    # Update submits which are not updated yet!
    for submit in data['submits'][Submit.SOURCE].filter(testing_status='in queue'):
        update_submit(submit)
    return data
