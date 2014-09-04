from trojsten.regal.contests.models import Round
from django.conf import settings
import os


def get_latest_rounds_by_competition():
    rounds = Round.objects.filter(
        visible=True
    ).order_by(
        'series__competition', 'end_time'
    ).distinct('series__competition')
    return {r.series.competition: r for r in rounds}


def _get_round_path(round, solution=False):
    round_dir = '{}{}'.format(round.number, settings.TASK_STATEMENTS_SUFFIX_ROUND)
    year_dir = '{}{}'.format(round.series.year, settings.TASK_STATEMENTS_SUFFIX_YEAR)
    competition_name = round.series.competition.name
    path_type = settings.TASK_STATEMENTS_SOLUTIONS_DIR if solution\
        else settings.TASK_STATEMENTS_TASKS_DIR
    path = os.path.join(
        settings.TASK_STATEMENTS_PATH,
        competition_name,
        year_dir,
        round_dir,
        path_type,
    )
    return path


def get_task_path(task, solution=False):
    task_file = '{}{}.html'.format(settings.TASK_STATEMENTS_PREFIX_TASK, task.number,)
    path = os.path.join(
        _get_round_path(task.round, solution),
        settings.TASK_STATEMENTS_HTML_DIR,
        task_file,
    )
    if os.path.exists(path):
        return path


def get_pdf_path(round, solution=False):
    pdf_file = settings.TASK_STATEMENTS_SOLUTIONS_PDF if solution\
        else settings.TASK_STATEMENTS_PDF
    path = os.path.join(
        _get_round_path(round, solution),
        pdf_file,
    )
    return path


def get_rounds_by_year():
    rounds = Round.objects.filter(visible=True).order_by('-series__year', '-number')
    rounds_dict = dict()
    for round in rounds:
        if not round.series.year in rounds_dict:
            rounds_dict[round.series.year] = list()
        rounds_dict[round.series.year].append(round)
    return rounds_dict
