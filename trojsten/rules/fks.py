from trojsten.results.generator import (CategoryTagKeyGeneratorMixin,
                                        ResultsGenerator)
from trojsten.results.representation import ResultsTag

from .default import FinishedRoundsResultsRulesMixin as FinishedRounds
from .default import CompetitionRules


FKS_A = 'A'
FKS_B = 'B'


class FKSResultsGenerator(
    CategoryTagKeyGeneratorMixin, ResultsGenerator
):

    def is_user_active(self, request, user):
        active = super(FKSResultsGenerator, self).is_user_active(request, user)
        if self.tag.key == FKS_B:
            # @FIXME: While the data needed to calculate whether user can solve
            # this category are not migrated, we use this hack.
            active = active and 0 == user.properties.filter(key__key_name="FKS starec").count()
        return active

    def deactivate_row_cells(self, request, row, cols):
        if self.tag.key == FKS_B:
            # Only best 4 of 5 task counted
            min(
                (row.cells_by_key[key] for key in row.cells_by_key),
                key=lambda cell: self.get_cell_total(request, cell)
            ).active = False


class FKSRules(FinishedRounds, CompetitionRules):

    RESULTS_TAGS = {
        FKS_B: ResultsTag(key=FKS_B, name='B'),
        FKS_A: ResultsTag(key=FKS_A, name='A'),
    }

    RESULTS_GENERATOR_CLASS = FKSResultsGenerator
