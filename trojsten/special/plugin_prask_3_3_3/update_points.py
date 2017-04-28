from trojsten.submit.constants import SUBMIT_TYPE_EXTERNAL
from trojsten.submit.models import Submit
from trojsten.contests.models import Task

from .models import UserLevel

TASK_ID = 1344


def get_task():
    try:
        return get_task._cache
    except AttributeError:
        get_task._cache = Task.objects.get(pk=TASK_ID)
        return get_task._cache


def update_points(user):
    uls = UserLevel.objects.filter(user=user.id)
    points = 0
    for ul in uls:
        points += {1: 2, 2: 3, 3: 4, 4: 6}.get(ul.level, 0)

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
