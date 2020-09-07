from django import template
from judge_client import constants as judge_constants

from trojsten.contests.models import Task
from trojsten.submit.forms import (
    DescriptionSubmitForm,
    SourceSubmitForm,
    TestableZipSubmitForm,
    TextSubmitForm,
)

from .. import constants
from ..models import Submit

register = template.Library()


@register.inclusion_tag("trojsten/submit/parts/submit_form.html", takes_context=True)
def show_submit_form(context, task, user, redirect, show_only_source=False):
    """Renders submit form for specified task"""
    context["task"] = task
    context["competition_ignored"] = user.is_competition_ignored(task.round.semester.competition)
    context["constants"] = constants
    context["redirect_to"] = redirect
    context["show_only_source"] = show_only_source
    if task.has_source:
        context["source_form"] = SourceSubmitForm()
    if task.has_description:
        context["description_form"] = DescriptionSubmitForm()
    if task.has_testablezip:
        context["testablezip_form"] = TestableZipSubmitForm()
    if task.has_text_submit:
        context["text_submit_form"] = TextSubmitForm()
    return context


@register.inclusion_tag("trojsten/submit/parts/submit_list.html")
def show_submit_list(task, user, show_only_source=False):
    """Renders submit list for specified task and user"""
    data = {"IN_QUEUE": constants.SUBMIT_STATUS_IN_QUEUE}
    data["task"] = task
    data["constants"] = constants
    data["show_only_source"] = show_only_source
    submits = Submit.objects.filter(task=task, user=user)

    # Hide reviewed descriptions when description_points_visible is disabled
    if not task.description_points_visible:
        submits = submits.exclude(
            submit_type=constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=constants.SUBMIT_STATUS_REVIEWED,
        )

    data["submits"] = {
        submit_type: submits.filter(submit_type=submit_type).order_by("-time")
        for submit_type, _ in constants.SUBMIT_TYPES
    }

    return data


@register.filter
def submitclass(submit):
    if submit.submit_type == constants.SUBMIT_TYPE_DESCRIPTION:
        if submit.testing_status == constants.SUBMIT_STATUS_REVIEWED:
            return "success"
        else:
            return ""
    else:
        if submit.testing_status == constants.SUBMIT_STATUS_IN_QUEUE:
            return "info submit-untested"
        elif submit.tester_response == judge_constants.SUBMIT_RESPONSE_OK:
            return "success submit-tested"
        elif submit.points > 0:
            return "warning submit-tested"
        else:
            return "danger submit-tested"


@register.inclusion_tag("trojsten/submit/parts/round_submit_form.html", takes_context=True)
def round_submit_form(context, round):
    """View, showing submit form for all tasks from round
    """
    tasks = Task.objects.filter(round=round).order_by("number")
    template_data = {"round": round, "tasks": tasks}
    context.update(template_data)
    return context


@register.inclusion_tag(
    "trojsten/submit/parts/submits_for_user_and_competition.html", takes_context=True
)
def show_submits_for_user_and_competition(context, competition):
    template_data = {"semesters": context["all_semesters"][competition][1:]}
    context.update(template_data)
    return context


@register.inclusion_tag(
    "trojsten/submit/parts/submits_for_user_and_semester.html", takes_context=True
)
def show_submits_for_user_and_semester(context, semester):
    template_data = {"rounds": reversed(semester.round_set.visible(context["user"]).all())}
    context.update(template_data)
    return context


@register.inclusion_tag("trojsten/submit/parts/submits_for_user_and_round.html", takes_context=True)
def show_submits_for_user_and_round(context, round):
    template_data = {
        "round_submits": context["all_submits"][round.semester.competition][round.semester][round]
    }
    context.update(template_data)
    return context
