# FIXME(generic_results_stage_2): Freezing the old, unsupported frozen results.
# New version of this file should simply use one manager function.


from django.contrib.auth.models import AnonymousUser
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from trojsten.contests.models import Round
from trojsten.results.helpers import make_result_table
from trojsten.results.models import FrozenResults, FrozenUserResult


class Command(BaseCommand):
    args = '<round_id round_id ...>'

    def freeze_result(self, frozen_results, tasks, result):
        frozen_result = FrozenUserResult.objects.create(
            frozenresults=frozen_results,
            original_user=result.user,
            rank=result.data.rank,
            prev_rank=result.data.prev_rank,
            fullname=result.user.get_full_name(),
            school_year=result.user.school_year,
            school=result.user.school,
            previous_points=result.data.previous_rounds_points,
            sum=result.data.sum,
        )

        for task in tasks:
            frozen_result.task_points.create(
                task=task,
                description_points=result.data.tasks[task.id].description_points,
                source_points=result.data.tasks[task.id].source_points,
                sum=result.data.tasks[task.id].sum,
            )

    @transaction.atomic
    def freeze_round(self, round, category, single_round):
        results_table = make_result_table(
            AnonymousUser(), round, category, single_round, force_generate=True
        )

        frozen_results = FrozenResults.objects.create(
            round=round,
            is_single_round=single_round,
            category=category,
            has_previous_results=results_table.has_previous_results,
        )

        for result in results_table.results_data:
            tasks = filter(
                lambda task: result.data.tasks[task.id].submitted,
                results_table.tasks,
            )

            self.freeze_result(frozen_results, tasks, result)

    def handle(self, *args, **options):
        for round_id in args:
            try:
                round = Round.objects.get(pk=int(round_id))
            except Round.DoesNotExist:
                raise CommandError('Round "%s" does not exist' % round_id)

            for single_round in (False, True):
                for category in [None] + list(round.categories):
                    self.freeze_round(round, category, single_round)

            self.stdout.write('Round "%s" successfully frozen' % round_id)
