from trojsten.contests.models import Task
from trojsten.submit.constants import SUBMIT_TYPE_EXTERNAL
from trojsten.submit.models import Submit

from .models import UserLevel

PERMONIK_TASK_ID = 1994


def get_task():
    try:
        return get_task._cache
    except AttributeError:
        get_task._cache = Task.objects.get(pk=PERMONIK_TASK_ID)
        return get_task._cache

def update_points(user):
    solved = UserLevel.objects.filter(user=user.id, solved=True)
    points = solved.count() * 1.5 - solved.filter(used_hint=True).count() * 0.5
    submit = Submit(
        task=get_task(),
        user=user,
        points=points,
        submit_type=SUBMIT_TYPE_EXTERNAL,
        testing_status="OK",
    )
    submit.save()

def mark_level_solved(user, level_id):
    userlevel, _ = UserLevel.objects.get_or_create(level_id=level_id, user=user)

    if not userlevel.solved:
        userlevel.solved = True
        userlevel.save()
        update_points(user)