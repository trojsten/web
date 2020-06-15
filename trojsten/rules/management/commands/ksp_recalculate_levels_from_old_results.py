# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.six import text_type

from trojsten.rules.ksp_levels import (
    level_updates_from_camp_attendance,
    level_updates_from_semester_results,
    prepare_events,
)
from trojsten.rules.models import KSPLevel


class Command(BaseCommand):
    help = (
        "Deletes KSP levels of all users and calculates new levels "
        "by simulating history (past camps and semesters)."
    )

    def handle(self, *args, **options):
        KSPLevel.objects.all().delete()

        # In the old results, tasks had 10, 10, 10, 15, 15, 20, 20, 20 points.
        # To get relevant historic results, limits must be set in dependence on the max. score.
        max_points_in_levels = {1: 120, 2: 140, 3: 160, 4: 180}

        # Events before the end of the school year 2016/2017
        for event in prepare_events(
            timezone.datetime(year=2017, month=6, day=30, tzinfo=timezone.get_default_timezone())
        ):
            if event.associated_semester is None:
                continue
            updates = list()
            if event.semester is not None:
                self.stdout.write(text_type(event.semester))
                level_up_score_thresholds = {
                    lvl: (x * 3) // 4 for lvl, x in max_points_in_levels.items()
                }
                updates = level_updates_from_semester_results(
                    event.semester, level_up_score_thresholds
                )
            elif event.camp is not None:
                self.stdout.write(text_type(event.camp))
                level_up_score_thresholds = {lvl: x // 2 for lvl, x in max_points_in_levels.items()}
                updates = level_updates_from_camp_attendance(
                    event.camp,
                    event.associated_semester,
                    event.last_semester_before_level_up,
                    level_up_score_thresholds,
                )
            self.stdout.write("\n".join(map(text_type, updates)))

            for update in updates:
                update.save()
