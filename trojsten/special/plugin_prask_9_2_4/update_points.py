from trojsten.contests.models import Task
from trojsten.submit.constants import SUBMIT_TYPE_EXTERNAL
from trojsten.submit.models import Submit

from .models import UserLevel

ZWARTE_DOOS_TASK_ID = 1555


def get_task():
    try:
        return get_task._cache
    except AttributeError:
        get_task._cache = Task.objects.get(pk=ZWARTE_DOOS_TASK_ID)
        return get_task._cache


def update_points(user):
    points = UserLevel.objects.filter(user=user, solved=True).count() * 10
    submit = Submit(
        task=get_task(),
        user=user,
        points=points,
        submit_type=SUBMIT_TYPE_EXTERNAL,
        testing_status="OK",
    )
    submit.save()
