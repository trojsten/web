# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import six
import shutil
from glob import glob

from django.utils.six.moves import input
from django.conf import settings
from django.core.management.base import NoArgsCommand

from trojsten.contests.models import Competition, Round, Semester


class Command(NoArgsCommand):
    help = 'Imports people and their related info from kaspar.'

    def handle_noargs(self, **options):
        # Compute changes
        move_paths = list()
        rounds = list()

        for competition in glob(os.path.join(settings.TASK_STATEMENTS_PATH, '*')):
            for year in glob(os.path.join(competition, '*rocnik')):
                for round in glob(os.path.join(year, '*kolo')):
                    new_path, round_obj = self.migrate_path(round)
                    move_paths.append((round, new_path))
                    if round_obj:
                        rounds.append(round_obj)

        # List changes
        print('Following paths are going to be moved:')
        print('\n'.join(('%s -> %s' % move for move in move_paths)))
        print('Following rounds are going to be renumbered:')
        print('\n'.join((six.text_type(r) for r in rounds)))
        # Ask and apply
        choice = input("Do you wish to proceed? [yN]:")
        if choice and choice[0].lower() == 'y':
            for src, dst in move_paths:
                shutil.move(src, dst)
            for round in rounds:
                round.save()

    def migrate_path(self, old_path):
        prefix, competition, year, round = old_path.rsplit('/', 3)
        year = ''.join(year[:-len('rocnik')])
        round = ''.join(round[:-len('kolo')])
        split = 3 if competition in {'UFO', 'FKS'} else 2
        semester = '1' if int(round) <= split else '2'

        round_obj = None
        if semester == '2':
            new_round = str(int(round) - split)
            try:
                competition_obj = Competition.objects.get(name=competition)
                semester_obj = Semester.objects.get(competition=competition_obj, year=year, number=semester)
                round_obj = Round.objects.get(number=round, semester=semester_obj)
                round_obj.number = int(new_round)
            except (Competition.DoesNotExist, Semester.DoesNotExist, Round.DoesNotExist) as e:
                print('%s not in DB: %s' % (old_path, e))
            round = new_round

        return os.path.join(prefix, competition, year, semester, round), round_obj
