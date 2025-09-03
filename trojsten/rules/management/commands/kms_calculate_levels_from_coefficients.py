# -*- coding: utf-8 -*-
import logging
from types import SimpleNamespace

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.six import text_type

from trojsten.contests.models import Round
from trojsten.people.models import User
from trojsten.rules.kms_old import KMS_BETA, KMSResultsGenerator, KMSRules
from trojsten.rules.models import KMSLevel
from trojsten.submit.models import Submit

logger = logging.getLogger("management_commands")


KMS_COEFFICIENT_TO_LEVEL = [1, 2, 3, 4, 4, 5]


class Command(BaseCommand):
    help = "Converts previous KMS coefficients to levels (when the new rules start to apply)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry",
            action="store_true",
            dest="dry",
            help="Only prints out the prepared level up events.",
        ),
        parser.add_argument(
            "--clear",
            action="store_true",
            dest="clear",
            help="Clear all level data before the beginning.",
        )

    def handle(self, *args, **options):
        if options["clear"] and not options["dry"]:
            KMSLevel.objects.all().delete()
        updates = []
        manager = KMSResultsGenerator(KMSRules.RESULTS_TAGS[KMS_BETA])
        active_users = Submit.objects.filter(
            task__round__semester__competition__name="KMS"
        ).values_list("user", flat=True).distinct()
        self.stdout.write("Active users: " + str(active_users))

        old_semester = (
            Round.objects.filter(
                semester__competition__name="KMS",
                start_time__lte=timezone.datetime(
                    year=2025, month=7, day=1, tzinfo=timezone.get_default_timezone()
                ),
            )
            .order_by("-start_time")
            .first()
            .semester
        )
        new_semester = SimpleNamespace(
            number=1,
            competition=old_semester.competition,
            year=old_semester.year + 1,
        )
        new_round = SimpleNamespace(
            number=1,
            semester=new_semester,
            start_time=timezone.now() - timezone.timedelta(1),
            end_time=timezone.now() + timezone.timedelta(1),
        )
        new_semester.start_time = new_round.start_time
        new_semester.end_time = new_round.end_time
        new_semester.round_set = [new_round]
        self.stdout.write("Last semester is" + str(old_semester))
        manager.prepare_coefficients(new_round)
        for user in active_users:
            user = User.objects.get(pk=user)
            level = KMS_COEFFICIENT_TO_LEVEL[min(5, manager.get_user_coefficient(user, new_round))]
            if level > 1:
                updates.append(
                    KMSLevel(
                        user=user,
                        new_level=min(5, level),
                        last_semester_before_level_up=old_semester,
                    )
                )

        self.stdout.write("\n".join(map(text_type, updates)))

        if not options["dry"]:
            for update in updates:
                update.save()
