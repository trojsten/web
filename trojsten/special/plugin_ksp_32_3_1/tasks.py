# -*- coding: utf-8 -*-

import json
import os
from subprocess import PIPE, Popen

from celery import shared_task

from trojsten.people.models import User
from trojsten.submit.constants import (SUBMIT_TYPE_EXTERNAL, SUBMIT_RESPONSE_OK,
                                       SUBMIT_STATUS_FINISHED)
from trojsten.submit.models import Submit
from trojsten.tasks.models import Task

from .constants import DATA_ROOT
from .models import LevelSolved, LevelSubmit


@shared_task
def process_submit(uid, sid, lid, l_submit_id, taskpoints, program, level_path):

    user = User.objects.get(pk=uid)
    level_submit = LevelSubmit.objects.get(pk=l_submit_id)

    with open(os.path.join(DATA_ROOT, level_path)) as f:
        level = json.load(f)

    test_script = os.path.join(DATA_ROOT, 'tester.sh')
    data = json.dumps({'program': program, 'level': level})
    p = Popen(['/usr/bin/env', 'bash', test_script], stdin=PIPE, stdout=PIPE)
    p.communicate(data)

    if p.returncode == 0:

        from .views import load_level_index
        index_data = load_level_index()

        level_submit.status = 'OK'

        LevelSolved.objects.get_or_create(user=user, series=sid, level=lid)

        for (task_id, _) in taskpoints:

            # Look if there are another series with same task_id and sum points
            points = 0
            _sid = 0
            for serie in index_data['series']:
                for (other_task_id, multiple) in serie['taskpoints']:
                    if task_id == other_task_id:
                        points += multiple * LevelSolved.objects.filter(
                            user=user, series=_sid).count()
                _sid += 1

            submit = Submit(
                task=Task.objects.get(pk=task_id),
                user=user,
                points=points,
                submit_type=SUBMIT_TYPE_EXTERNAL,
                filepath='',
                testing_status=SUBMIT_STATUS_FINISHED,
                tester_response=SUBMIT_RESPONSE_OK,
                protocol_id='',
            )
            submit.save()
    else:
        level_submit.status = 'WA'

    level_submit.save()
