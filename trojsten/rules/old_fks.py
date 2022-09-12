from trojsten.results.generator import CategoryTagKeyGeneratorMixin, ResultsGenerator
from trojsten.results.representation import ResultsTag

from .default import CompetitionRules

FKS_A = "A"
FKS_B = "B"


class FKSResultsGenerator(CategoryTagKeyGeneratorMixin, ResultsGenerator):
    def is_user_active(self, request, user):
        active = super(FKSResultsGenerator, self).is_user_active(request, user)

        # FIXME(generic_results_stage_2): Hacking backward compatibility, since there is no
        # results freezing yet.
        if request.round.semester.pk == 9:
            if self.tag.key == FKS_B:
                STARCI = [
                    115,
                    92,
                    4447,
                    4512,
                    4350,
                    5,
                    4471,
                    4507,
                    130,
                    4513,
                    40,
                    4499,
                    4450,
                    4404,
                    4668,
                ]
                return active and user.pk not in STARCI

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
                key=lambda cell: self.get_cell_total(request, cell),
            ).active = False

        # FIXME(generic_results_stage_2): Hacking backward compatibility, since there is no
        # results freezing yet.
        if self.tag.key == FKS_A:
            if request.round.semester.pk == 9:
                row.active = (row.previous and row.previous.active) or [
                    key for key in (6, 7) if row.cells_by_key[key].manual_points is not None
                ]

    @staticmethod
    def get_actual_result_rounds(competition):
        return None


class FKSRules(CompetitionRules):

    RESULTS_TAGS = {FKS_B: ResultsTag(key=FKS_B, name="B"), FKS_A: ResultsTag(key=FKS_A, name="A")}

    RESULTS_GENERATOR_CLASS = FKSResultsGenerator
