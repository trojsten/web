# -*- coding: utf-8 -*-
import logging

from django.core.management.base import BaseCommand
from django.utils.six import text_type

from trojsten.contests.models import Round, Semester
from trojsten.events.models import Event
from trojsten.rules.fks_levels import (
    level_updates_from_camp_attendance,
    level_updates_from_semester_results,
)

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    help = "Adds FKS level updates resulting from a camp or a semester."

    # TODO: Automate level updates. Run this when freezing the results.

    def add_arguments(self, parser):
        parser.add_argument("camp_or_semester", type=str, choices=["camp", "semester"])
        parser.add_argument("id", type=int, help="Semester or camp id.")
        parser.add_argument(
            "--dry",
            action="store_true",
            dest="dry",
            help="Only prints out the prepared level up events.",
        )

    def handle(self, *args, **options):
        updates = []
        if options["camp_or_semester"] == "camp":
            try:
                camp = Event.objects.get(pk=options["id"])
            except Event.DoesNotExist:
                logger.error("No event with id {} found.".format(options["id"]))
                return

            rounds_with_semesters = (
                Round.objects.filter(
                    semester__competition__name="FKS", start_time__lte=camp.start_time
                )
                .order_by("-semester", "start_time", "pk")
                .distinct("semester")
                .select_related("semester")
            )

            # Semester that was running in the same time as the camp.
            # If no semester was running during the camp, the last running semester at the time.
            # For this semester the levels remain unchanged.
            last_semester_before_level_up = rounds_with_semesters[0].semester
            # The semester from which the participants were invited.
            associated_semester = camp.semester

            updates = level_updates_from_camp_attendance(
                camp, associated_semester, last_semester_before_level_up
            )

        elif options["camp_or_semester"] == "semester":
            try:
                semester = Semester.objects.get(pk=options["id"])
            except Semester.DoesNotExist:
                logger.error("No semester with id {} found.".format(options["id"]))
                return
            updates = level_updates_from_semester_results(semester)

        self.stdout.write("\n".join(map(text_type, updates)))

        if not options["dry"]:
            for update in updates:
                update.save()
