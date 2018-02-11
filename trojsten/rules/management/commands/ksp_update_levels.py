# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils.six import text_type

from trojsten.rules.ksp_levels import level_updates_from_camp_attendance, level_updates_from_semester_results
from trojsten.contests.models import Semester, Round
from trojsten.events.models import Event


class Command(BaseCommand):
    help = 'Adds KSP level updates based on a camp or a semester.'

    def add_arguments(self, parser):
        parser.add_argument('camp_or_semester', type=str, choices=['camp', 'semester'])
        parser.add_argument('id', type=int, help='Semester or camp id.')
        parser.add_argument('--dry', action='store_false', dest='dry',
                            help='Only prints out the prepared level up events.')

    def handle(self, *args, **options):
        updates = []
        if options['camp_or_semester'] == 'camp':
            camp = Event.objects.get(options['id'])
            if camp is None:
                self.stderr.write('No event with id {} found.'.format(options['id']))

            rounds_with_semesters = Round.objects.filter(
                semester__competition__name='KSP', start_time__lte=camp.start_time
            ).order_by(
                'semester', 'start_time', 'pk'
            ).distinct(
                'semester'
            ).select_related('semester')

            # Semester that was running in the same time as the camp. For this semester the levels remain unchanged.
            last_semester_before_level_up = rounds_with_semesters[-1].semester
            # The semester from which the participants were invited.
            associated_semester = rounds_with_semesters[-2].semester

            updates = level_updates_from_camp_attendance(camp, associated_semester, last_semester_before_level_up)

        elif options['camp_or_semester'] == 'semester':
            semester = Semester.objects.get(options['id'])
            if semester is None:
                self.stderr.write('No semester with id {} found.'.format(options['id']))
            updates = level_updates_from_semester_results(semester)

        self.stdout.write('\n'.join(map(text_type, updates)))

        if not options['dry']:
            for update in updates:
                update.save()
