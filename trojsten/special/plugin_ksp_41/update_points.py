from trojsten.contests.models import Task
from trojsten.submit.constants import SUBMIT_TYPE_EXTERNAL
from trojsten.submit.models import Submit

from .models import UserLevel

KSP_FUNKCIE_TASK_ID = 2815
PRASK_FUNKCIE_TASK_ID = 2820


def get_task(prask=False):
    if prask:
        return Task.objects.get(pk=PRASK_FUNKCIE_TASK_ID)
    else:
        return Task.objects.get(pk=KSP_FUNKCIE_TASK_ID)


def update_points(user, prask=False):
    points = UserLevel.objects.filter(user=user, solved=True, level_gte=20).count()
    points += UserLevel.objects.filter(user=user, solved=True, level=28).count()
    if prask:
        points = points * 5
    submit = Submit(
        task=get_task(prask),
        user=user,
        points=points,
        submit_type=SUBMIT_TYPE_EXTERNAL,
        testing_status="OK",
    )
    submit.save()
