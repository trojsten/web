from django import template

from trojsten.old_submit.forms import (DescriptionSubmitForm, SourceSubmitForm,
                                       TestableZipSubmitForm)
from trojsten.contests.models import Task

from .. import constants
from ..models import Submit

register = template.Library()


@register.inclusion_tag('trojsten/old_submit/parts/submit_form.html')
def show_submit_form(task, redirect):
    """Renders submit form for specified task"""
    data = {}
    data['task'] = task
    data['constants'] = constants
    data['redirect_to'] = redirect
    if task.has_source:
        data['source_form'] = SourceSubmitForm()
    if task.has_description:
        data['description_form'] = DescriptionSubmitForm()
    if task.has_testablezip:
        data['testablezip_form'] = TestableZipSubmitForm()
    return data


@register.inclusion_tag('trojsten/old_submit/parts/submit_list.html')
def show_submit_list(task, user):
    """Renders submit list for specified task and user"""
    data = {'IN_QUEUE': constants.SUBMIT_STATUS_IN_QUEUE}
    data['task'] = task
    data['constants'] = constants
    submits = Submit.objects.filter(task=task, user=user)
    data['submits'] = {
        submit_type: submits.filter(submit_type=submit_type).order_by('-time')
        for submit_type, _ in constants.SUBMIT_TYPES
    }

    return data


@register.filter
def submitclass(submit):
    if submit.testing_status == constants.SUBMIT_STATUS_IN_QUEUE:
        return 'info submit-untested'
    elif submit.tester_response == constants.SUBMIT_RESPONSE_OK:
        return 'success submit-tested'
    elif submit.points > 0:
        return 'warning submit-tested'
    else:
        return 'danger submit-tested'


@register.inclusion_tag('trojsten/old_submit/parts/round_submit_form.html', takes_context=True)
def round_submit_form(context, round):
    """View, showing submit form for all tasks from round
    """
    tasks = Task.objects.filter(round=round).order_by('number')
    template_data = {'round': round, 'tasks': tasks}
    context.update(template_data)
    return context
