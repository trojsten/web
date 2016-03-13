# -*- coding: utf-8 -*-

# @TODO: Temporary file used to demonstrate the functionality while developing

from django.core.management.base import BaseCommand, CommandError

from trojsten.regal.contests.models import Round
from trojsten.results.manager import get_results


class Command(BaseCommand):
    args = '<round_id single_round?>'

    def handle(self, round_id, single_round=False, **kwargs):
        try:
            round = Round.objects.get(pk=int(round_id))
        except Round.DoesNotExist:
            raise CommandError('Round "%s" does not exist' % round_id)

        results = get_results("", round, bool(single_round))

        for row in results.iterrows():
            self.stdout.write('%s: %s\n' % (row.name, str(row.total)))
