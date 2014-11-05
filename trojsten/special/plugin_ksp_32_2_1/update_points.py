from .models import UserLevel
from trojsten.regal.tasks.models import Submit, Task

from .models import UserLevel
from trojsten.regal.tasks.models import Submit, Task


# @TODO(sysel): update for Zwarte doos 2
ZWARTE_DOOS_TASK_ID = 972


def get_task():
    try:
        return get_task._cache
    except AttributeError:
        get_task._cache = Task.objects.get(pk=ZWARTE_DOOS_TASK_ID)
        return get_task._cache


def update_points(user):
    points = UserLevel.objects.filter(user=user.id, solved=True).count()
    submit = Submit(
        task=get_task(),
        user=user,
        points=points,
        submit_type=Submit.EXTERNAL,
        filepath="",
        testing_status="OK",
        tester_response="",
        protocol_id="",
    )
    submit.save()


