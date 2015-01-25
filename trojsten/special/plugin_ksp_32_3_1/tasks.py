# -*- coding: utf-8 -*-

import json
import os
from subprocess import Popen, PIPE

from trojsten.regal.people.models import User
from trojsten.regal.tasks.models import Submit
from trojsten.regal.tasks.models import Task

from celery import shared_task

from .models import LevelSolved, LevelSubmit
from .constants import DATA_ROOT


@shared_task
def process_submit(uid, sid, lid, submit_id, taskpoints, program, level_path):

    user = User.objects.get(pk=uid)
    submit = LevelSubmit.objects.get(pk=submit_id)

    with open(os.path.join(DATA_ROOT, level_path)) as f:
        level = json.load(f)

    test_script = os.path.join(DATA_ROOT, "tester.sh")
    data = json.dumps({"program":program, "level":level })
    result, _ = Popen(
        ["/bin/bash", test_script],
        stdin=PIPE, stdout=PIPE).communicate(data)

    if result == "OK\n":
        submit.status = "OK"

        LevelSolved.objects.get_or_create(user=user, series=sid, level=lid)

        points = LevelSolved.objects.filter(user=user, series=sid).count()

        for (task_id, multiple) in taskpoints:

            real_submit = Submit(
                task=Task.objects.get(pk=task_id),
                user=user,
                points=points*multiple,
                submit_type=Submit.EXTERNAL,
                filepath="",
                testing_status="OK",
                tester_response="",
                protocol_id="",
            )
            real_submit.save()
    else:
        submit.status = "WA"

    submit.save()
