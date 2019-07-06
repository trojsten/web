from decimal import Decimal

from django.db.models import Sum

from trojsten.results.generator import (
    BonusColumnGeneratorMixin,
    PrimarySchoolGeneratorMixin,
    ResultsGenerator,
)

from .default import FinishedRoundsResultsRulesMixin as FinishedRounds
from .default import CompetitionRules


class UFOResultsGenerator(PrimarySchoolGeneratorMixin, BonusColumnGeneratorMixin, ResultsGenerator):
    def create_empty_results(self, request):
        res = super(UFOResultsGenerator, self).create_empty_results(request)

        request.max_points = sum(
            request.round.task_set.aggregate(
                x=Sum("description_points"), y=Sum("source_points")
            ).values()
        )

        return res

    def calculate_row_round_total(self, request, row, cols):
        super(UFOResultsGenerator, self).calculate_row_round_total(request, row, cols)
        r = 9 - (row.user.graduation - self.get_minimal_year_of_graduation(request, row.user))
        self.bonus = (
            row.round_total
            * (request.max_points - row.round_total)
            * (Decimal("0.000") if r == 9 else Decimal("0.008") if r == 8 else Decimal("0.015"))
        )

        # FIXME(generic_results_stage_2): Hacking backward compatibility, since there is no
        # results freezing yet.
        if request.round.semester.pk == 10:
            self.bonus = (request.max_points - row.round_total) * (
                Decimal("0.000") if r == 9 else Decimal("0.008") if r == 8 else Decimal("0.015")
            )

        row.round_total += self.bonus


class UFORules(FinishedRounds, CompetitionRules):

    RESULTS_GENERATOR_CLASS = UFOResultsGenerator
