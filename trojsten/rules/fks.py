from trojsten.results.generator import (CategoryTagKeyGeneratorMixin,
                                        ResultsGenerator)
from trojsten.results.representation import ResultsTag

from .default import CompetitionRules


class FKSResultsGenerator(
    CategoryTagKeyGeneratorMixin, ResultsGenerator
):

    def is_user_active(self, request, user):
        active = super(FKSResultsGenerator, self).is_user_active(request, user)
        if self.tag.key == 'B':
            # @FIXME: While the data needed to calculate whether user can solve
            # this category are not migrated, we use this hack.
            active = active and 0 == user.properties.filter(key__key_name="FKS starec").count()
        return active

    def deactivate_row_cells(self, request, row, cols):
        if self.tag.key == 'B':
            # Only best 4 of 5 task counted
            min(
                (row.cells_by_key[key] for key in row.cells_by_key),
                key=lambda cell: self.get_cell_total(request, cell)
            ).active = False

            # User must have sloved at least one only B task:
            row.active = row.previous is not None and row.previous.active
            if not row.active:
                for key in (1, 2, 3):
                    if row.cells_by_key[key].manual_points is not None:
                        row.active = True
                        break
                    if row.cells_by_key[key].auto_points is not None:
                        row.active = True
                        break


class FKSRules(CompetitionRules):

    RESULTS_TAGS = {
        'B': ResultsTag(key='B', name='B'),
        'A': ResultsTag(key='A', name='A'),
    }

    RESULTS_GENERATOR_CLASS = FKSResultsGenerator
