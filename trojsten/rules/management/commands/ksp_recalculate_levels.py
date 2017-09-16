# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils.six import text_type

from trojsten.rules.models import KSPLevel
from trojsten.rules.ksp_levels import prepare_events, level_updates_from_camp_attendance, \
    level_updates_from_semester_results


class Command(BaseCommand):
    help = 'Deletes KSP levels of all users and calculates new levels ' \
           'by simulating history (past camps and semesters).'
    # TODO: Maybe add command that incrementally updates levels as a result of the most recent events or automate
    # level updates.

    def handle(self, *args, **options):
        KSPLevel.objects.all().delete()

        for event in prepare_events():
            if event.associated_semester is None:
                continue
            updates = list()
            if event.semester is not None:
                self.stdout.write(text_type(event.semester))
                updates = level_updates_from_semester_results(event.semester)
            elif event.camp is not None:
                self.stdout.write(text_type(event.camp))
                updates = level_updates_from_camp_attendance(event.camp, event.associated_semester,
                                                             event.last_semester_before_level_up)
            self.stdout.write('\n'.join(map(text_type, updates)))

            for update in updates:
                update.save()
