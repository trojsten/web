from .models import UserLevel
from trojsten.regal.tasks.models import Submit, Task


TASK_ID = 1085


def get_task():
    try:
        return get_task._cache
    except AttributeError:
        get_task._cache = Task.objects.get(pk=TASK_ID)
        return get_task._cache


def update_points(user):
    points = 2*UserLevel.objects.filter(user=user.id, level__lte=3).count()
    points += 3*UserLevel.objects.filter(user=user.id, level__gte=4).count()
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
