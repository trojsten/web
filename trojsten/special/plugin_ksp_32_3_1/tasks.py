# -*- coding: utf-8 -*-

import json
import os
from subprocess import Popen, PIPE

from trojsten.regal.people.models import User
from trojsten.regal.tasks.models import Submit
from trojsten.regal.tasks.models import Task
from trojsten.submit.constants import SUBMIT_STATUS_FINISHED, SUBMIT_RESPONSE_OK

from celery import shared_task

from .models import LevelSolved, LevelSubmit
from .constants import DATA_ROOT


@shared_task
def process_submit(uid, sid, lid, l_submit_id, taskpoints, program, level_path):

    user = User.objects.get(pk=uid)
    level_submit = LevelSubmit.objects.get(pk=l_submit_id)

    with open(os.path.join(DATA_ROOT, level_path)) as f:
        level = json.load(f)

    test_script = os.path.join(DATA_ROOT, "tester.sh")
    data = json.dumps({"program": program, "level": level})
    p = Popen( ["/bin/bash", test_script], stdin=PIPE, stdout=PIPE)
    p.communicate(data)

    if p.returncode == 0:
        level_submit.status = "OK"

        LevelSolved.objects.get_or_create(user=user, series=sid, level=lid)
        points = LevelSolved.objects.filter(user=user, series=sid).count()

        for (task_id, multiple) in taskpoints:

            submit = Submit(
                task=Task.objects.get(pk=task_id),
                user=user,
                points=points*multiple,
                submit_type=Submit.EXTERNAL,
                filepath="",
                testing_status=SUBMIT_STATUS_FINISHED,
                tester_response=SUBMIT_RESPONSE_OK,
                protocol_id="",
            )
            submit.save()
    else:
        level_submit.status = "WA"

    level_submit.save()
