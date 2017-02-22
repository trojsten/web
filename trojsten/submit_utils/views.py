# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from trojsten.contests.models import Competition, Round, Task


@login_required
def task_submit_page(request, task_id):
    """View, ktory zobrazi formular na odovzdanie a zoznam submitov
    prave prihlaseneho cloveka pre danu ulohu"""
    task = get_object_or_404(Task, pk=task_id)
    template_data = {'task': task}
    return render(request, 'trojsten/submit_utils/task_submit.html', template_data)


@login_required
def round_submit_page(request, round_id):
    """View, ktorý zobrazí formuláre pre odovzdanie pre všetky úlohy
    z daného kola"""
    round = get_object_or_404(Round, pk=round_id)
    template_data = {'round': round}
    return render(request, 'trojsten/submit_utils/round_submit.html', template_data)


@login_required
def active_rounds_submit_page(request):
    rounds = Round.objects.active_visible(request.user).order_by('end_time')
    competitions = Competition.objects.current_site_only()
    template_data = {
        'rounds': rounds,
        'competitions': competitions,
    }
    return render(
        request,
        'trojsten/submit_utils/active_rounds_submit.html',
        template_data,
    )
