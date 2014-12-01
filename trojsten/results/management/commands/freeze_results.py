from django.core.management.base import BaseCommand, CommandError

from trojsten.regal.contests.models import Round
from trojsten.results.models import FrozenResults


class Command(BaseCommand):
    args = '<round_id round_id ...>'

    def handle(self, *args, **options):
        for round_id in args:
            try:
                round = Round.objects.get(pk=int(round_id))
            except Round.DoesNotExist:
                raise CommandError('Round "%s" does not exist' % round_id)

            for single_round in (False, True):
                for category in [None] + list(round.categories):
                    frozen_results = FrozenResults.objects.create(
                        round=round,
                        is_single_round=single_round,
                        category=category
                    )
                    frozen_results.save()

            self.stdout.write('Round "%s" successfully frozen' % round_id)
