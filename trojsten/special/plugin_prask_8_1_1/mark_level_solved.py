from functools import lru_cache

from trojsten.contests.models import Task
from trojsten.submit.constants import SUBMIT_TYPE_EXTERNAL
from trojsten.submit.models import Submit

from .models import UserLevel


@lru_cache(maxsize=1)
def get_task(task_id):
    return Task.objects.get(pk=task_id)


def update_points(task_id, user, series_id, points_per_level):
    solved = UserLevel.objects.filter(user=user.id, series=series_id)
    points = solved.count() * points_per_level
    submit = Submit(
        task=get_task(task_id),
        user=user,
        points=points,
        submit_type=SUBMIT_TYPE_EXTERNAL,
        testing_status="OK",
    )
    submit.save()


def mark_level_solved(task_id, user, series_id, level_id, points_per_level):
    userlevel, _ = UserLevel.objects.get_or_create(user=user, series=series_id, level=level_id)
    update_points(task_id, user, series_id, points_per_level)
