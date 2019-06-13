from trojsten.submit.constants import SUBMIT_TYPE_EXTERNAL
from trojsten.submit.models import Submit
from trojsten.contests.models import Task

from .models import UserLevel

TASK_ID = 1177


def get_task():
    try:
        return get_task._cache
    except AttributeError:
        get_task._cache = Task.objects.get(pk=TASK_ID)
        return get_task._cache


def update_points(user):
    points = 4 * UserLevel.objects.filter(user=user.id, level=1).count()
    points += 5 * UserLevel.objects.filter(user=user.id, level=2).count()
    points += 6 * UserLevel.objects.filter(user=user.id, level=3).count()
    submit = Submit(
        task=get_task(),
        user=user,
        points=points,
        submit_type=SUBMIT_TYPE_EXTERNAL,
        filepath="",
        testing_status="OK",
        tester_response="",
        protocol_id="",
    )
    submit.save()
