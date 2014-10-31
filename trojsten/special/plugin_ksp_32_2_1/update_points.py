from .models import UserLevel
from trojsten.regal.tasks.models import Submit, Task

try:
    TASK = Task.objects.get()
except Exception:
    pass


def update_points(user):
    print("user")
    points = len(UserLevel.objects.filter(user=user.id, solved=True))
    submit = Submit(
        task=TASK,
        user=user,
        points=points,
        submit_type=Submit.DESCRIPTION,
        filepath="",
        testing_status="OK",
        tester_response="",
        protocol_id="",
    )
    submit.save()


