# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from trojsten.rules.models import KSPLevel
from trojsten.rules.ksp_levels import prepare_events, level_updates_from_camp_attendance, \
    level_updates_from_semester_results


class Command(BaseCommand):
    help = 'Deletes KSP levels of all users and calculates new levels by simulating history (past camps and semesters).'
    # TODO: Maybe add command that incrementally updates levels as a result of the most recent events or automate
    # level updates.

    def handle(self, *args, **options):
        KSPLevel.objects.all().delete()

        for event in prepare_events():
            if event.associated_semester is None:
                continue
            updates = list()
            if event.semester is not None:
                updates = level_updates_from_semester_results(event.semester)
            elif event.camp is not None:
                updates = level_updates_from_camp_attendance(event.camp, event.associated_semester,
                                                             event.last_semester_before_level_up)
            print(event)
            print('\n'.join(map(unicode, updates)))

            for update in updates:
                update.save()
