# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.six import text_type


from trojsten.rules.ksp_levels import level_updates_from_camp_attendance, level_updates_from_semester_results
from trojsten.contests.models import Semester, Round
from trojsten.events.models import Event


class Command(BaseCommand):
    help = 'Adds KSP level updates resulting from a camp or a semester.'
    # TODO: Automate level updates.

    def add_arguments(self, parser):
        parser.add_argument('camp_or_semester', type=str, choices=['camp', 'semester'])
        parser.add_argument('id', type=int, help='Semester or camp id.')
        parser.add_argument('--dry', action='store_false', dest='dry',
                            help='Only prints out the prepared level up events.')

    def handle(self, *args, **options):
        updates = []
        if options['camp_or_semester'] == 'camp':
            camp = Event.objects.get(pk=options['id'])
            if camp is None:
                self.stderr.write('No event with id {} found.'.format(options['id']))

            rounds_with_semesters = Round.objects.filter(
                semester__competition__name='KSP', start_time__lte=camp.start_time
            ).order_by(
                '-semester', 'start_time', 'pk'
            ).distinct(
                'semester'
            ).select_related('semester')

            # Semester that was running in the same time as the camp. For this semester the levels remain unchanged.
            last_semester_before_level_up = rounds_with_semesters[0].semester
            # The semester from which the participants were invited.
            associated_semester = rounds_with_semesters[1].semester

            new_rules_start = timezone.datetime(year=2017, month=9, day=1, tzinfo=timezone.get_default_timezone())
            associated_semester_from_old_rules = rounds_with_semesters[1].end_time < new_rules_start
            max_points_in_levels = {1: 120, 2: 140, 3: 160, 4: 180} if associated_semester_from_old_rules else None

            updates = level_updates_from_camp_attendance(camp, associated_semester, last_semester_before_level_up,
                                                         {l: x // 2 for l, x in max_points_in_levels.items()})

        elif options['camp_or_semester'] == 'semester':
            semester = Semester.objects.get(pk=options['id'])
            if semester is None:
                self.stderr.write('No semester with id {} found.'.format(options['id']))
            updates = level_updates_from_semester_results(semester)

        self.stdout.write('\n'.join(map(text_type, updates)))

        if not options['dry']:
            for update in updates:
                update.save()
