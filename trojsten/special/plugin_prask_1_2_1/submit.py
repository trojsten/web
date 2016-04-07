from django.db.models import Sum

from trojsten.tasks.models import Submit, Task
from trojsten.submit.constants import SUBMIT_STATUS_FINISHED
from trojsten.submit.constants import SUBMIT_RESPONSE_OK

from .models import UserCategory


TASK_ID = 1013


def update_points(user):
    aggr = UserCategory.objects.filter(user=user).aggregate(sum=Sum('points'))
    submit = Submit(
        task=Task.objects.get(pk=TASK_ID),
        user=user,
        points=aggr['sum'],
        submit_type=Submit.EXTERNAL,
        filepath='',
        testing_status=SUBMIT_STATUS_FINISHED,
        tester_response=SUBMIT_RESPONSE_OK,
        protocol_id='',
    )
    submit.save()
