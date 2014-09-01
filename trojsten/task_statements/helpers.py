from trojsten.regal.contests.models import Round
from django.conf import settings
import os


def get_latest_round():
    return Round.objects.filter(visible=True).order_by('end_time')[0]


def get_task_path(task, solution=False):
    task_file = '{}{}.html'.format(settings.TASK_STATEMENTS_PREFIX_TASK, task.number,)
    round_dir = '{}{}'.format(task.round.number, settings.TASK_STATEMENTS_SUFFIX_ROUND)
    year_dir = '{}{}'.format(task.round.series.year, settings.TASK_STATEMENTS_SUFFIX_YEAR)
    competition_name = task.round.series.competition.name
    path_type = settings.TASK_STATEMENTS_SUFFIX_SOLUTIONS if solution\
        else settings.TASK_STATEMENTS_TASKS_DIR
    path = os.path.join(
        settings.TASK_STATEMENTS_PATH,
        competition_name,
        year_dir,
        round_dir,
        path_type,
        settings.TASK_STATEMENTS_HTML_DIR,
        task_file,
    )
    print path
    if os.path.exists(path):
        return path
