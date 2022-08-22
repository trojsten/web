# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from news.models import Entry as NewsEntry
from sendfile import sendfile
from wiki.decorators import get_article

from trojsten.contests.models import Competition, Round, Task
from trojsten.rules.susi_constants import SUSI_COMPETITION_ID
from trojsten.utils.utils import is_true

from . import constants


@get_article(can_read=True)
def archive(request, article, *args, **kwargs):
    kwargs.update({"article": article})
    return render(request, "trojsten/contests/archive.html", kwargs)


def _statement_view(request, task_id, solution=False):
    task = get_object_or_404(Task, pk=task_id)
    if not task.visible(request.user) or (solution and not task.solution_visible(request.user)):
        raise Http404
    template_data = {"task": task, "SUSI_COMPETITION_ID": SUSI_COMPETITION_ID}
    if task.task_file_exists:
        with settings.TASK_STATEMENTS_STORAGE.open(task.get_path(solution=False)) as f:
            template_data["task_text"] = f.read().decode()

    if solution and task.solution_file_exists:
        with settings.TASK_STATEMENTS_STORAGE.open(task.get_path(solution=True)) as f:
            template_data["solution_text"] = f.read().decode()
    return render(
        request,
        "trojsten/contests/view_{}_statement.html".format("solution" if solution else "task"),
        template_data,
    )


def task_statement(request, task_id):
    return _statement_view(request, task_id, solution=False)


def solution_statement(request, task_id):
    return _statement_view(request, task_id, solution=True)


def task_list(request, round_id):
    round = get_object_or_404(Round.objects.visible(request.user), pk=round_id)
    competitions = Competition.objects.current_site_only()
    template_data = {
        "round": round,
        "competitions": competitions,
        "susi_is_discovery": round.susi_is_discovery,
    }
    return render(request, "trojsten/contests/list_tasks.html", template_data)


def active_rounds_task_list(request):
    rounds = Round.objects.active_visible(request.user).order_by("end_time")
    competitions = Competition.objects.current_site_only()
    template_data = {"rounds": rounds, "competitions": competitions}
    return render(request, "trojsten/contests/list_active_rounds_tasks.html", template_data)


def view_pdf(request, round_id, solution=False):
    round = get_object_or_404(Round.objects.visible(request.user), pk=round_id)
    if solution and not round.solutions_are_visible_for_user(request.user):
        raise Http404
    path = round.get_pdf_path(solution)
    if settings.TASK_STATEMENTS_STORAGE.exists(path):
        try:
            response = sendfile(request, settings.TASK_STATEMENTS_STORAGE.path(path))
            response["Content-Disposition"] = 'inline; filename="%s"' % round.get_pdf_name(solution)
            return response
        except NotImplementedError:
            return redirect(settings.TASK_STATEMENTS_STORAGE.url(path))
    else:
        raise Http404


def show_picture(request, type, task_id, picture):
    task = get_object_or_404(Task, pk=task_id)
    if not task.visible(request.user):
        raise Http404
    _, ext = os.path.splitext(picture)
    if ext not in settings.ALLOWED_PICTURE_EXT:
        raise Http404
    path = os.path.join(task.round.get_pictures_path(), picture)
    if settings.TASK_STATEMENTS_STORAGE.exists(path):
        try:
            return sendfile(request, settings.TASK_STATEMENTS_STORAGE.path(path))
        except NotImplementedError:
            return redirect(settings.TASK_STATEMENTS_STORAGE.url(path))
    else:
        raise Http404


def ajax_progressbar(request, round_id):
    round = get_object_or_404(Round.objects.visible(request.user), pk=round_id)
    template_data = {"round": round, "results": is_true(request.GET.get("results", False))}
    return render(request, "trojsten/contests/ajax/progress.html", template_data)


def dashboard(request):
    rounds = Round.objects.active_visible(request.user).order_by("end_time")
    competitions = Competition.objects.current_site_only()
    news = (
        NewsEntry.objects.filter(sites__id=settings.SITE_ID)
        .select_related("author")
        .prefetch_related("tags")
        .all()[: constants.NEWS_ENTRIES_ON_DASHBOARD]
    )

    return render(
        request,
        "trojsten/contests/dashboard.html",
        {"competitions": competitions, "rounds": rounds, "news_entries": news},
    )
