from django.db.models import Sum
from judge_client.constants import SUBMIT_RESPONSE_OK

from trojsten.contests.models import Task
from trojsten.submit.constants import SUBMIT_STATUS_FINISHED, SUBMIT_TYPE_EXTERNAL
from trojsten.submit.models import Submit

from .models import UserCategory

TASK_ID = 1013


def update_points(user):
    aggr = UserCategory.objects.filter(user=user).aggregate(sum=Sum("points"))
    submit = Submit(
        task=Task.objects.get(pk=TASK_ID),
        user=user,
        points=aggr["sum"],
        submit_type=SUBMIT_TYPE_EXTERNAL,
        filepath="",
        testing_status=SUBMIT_STATUS_FINISHED,
        tester_response=SUBMIT_RESPONSE_OK,
        protocol_id="",
    )
    submit.save()
