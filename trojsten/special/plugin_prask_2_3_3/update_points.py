from .models import UserLevel
from trojsten.tasks.models import Submit, Task


TASK_ID = 1145


def get_task():
    try:
        return get_task._cache
    except AttributeError:
        get_task._cache = Task.objects.get(pk=TASK_ID)
        return get_task._cache


def update_points(user):
    points = 3*UserLevel.objects.filter(user=user.id, level=1).count()
    points += 5*UserLevel.objects.filter(user=user.id, level=2).count()
    points += 7*UserLevel.objects.filter(user=user.id, level=3).count()
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
