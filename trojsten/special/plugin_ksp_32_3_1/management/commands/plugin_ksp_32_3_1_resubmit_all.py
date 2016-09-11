# -*- coding: utf-8 -*-

from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db.models import Count

from trojsten.people.models import User
from trojsten.submit.constants import (SUBMIT_TYPE_EXTERNAL, SUBMIT_RESPONSE_OK,
                                       SUBMIT_STATUS_FINISHED)
from trojsten.submit.models import Submit
from trojsten.contests.models import Task

from ...models import LevelSolved
from ...views import load_level_index


class Command(BaseCommand):
    help = 'Creates a new submit for each user that ever solved ZergBot'

    def handle(self, *args, **options):
        data = load_level_index()
        points = defaultdict(lambda: defaultdict(lambda: 0))
        semester_id = 0
        for serie in data['semester']:
            solved_semester = LevelSolved.objects.filter(
                semester=semester_id
            ).values('user').annotate(count=Count('level'))

            for solved_serie in solved_semester:
                for (task_id, multiple) in serie['taskpoints']:
                    points[solved_serie['user']][task_id] += (
                        solved_serie['count'] * multiple
                    )

            semester_id += 1

        for uid in points:
            for task_id in points[uid]:
                submit = Submit(
                    task=Task.objects.get(pk=task_id),
                    user=User.objects.get(pk=uid),
                    points=points[uid][task_id],
                    submit_type=SUBMIT_TYPE_EXTERNAL,
                    filepath='',
                    testing_status=SUBMIT_STATUS_FINISHED,
                    tester_response=SUBMIT_RESPONSE_OK,
                    protocol_id='',
                )
                submit.save()
