from trojsten.results.constants import COEFFICIENT_COLUMN_KEY
from trojsten.results.generator import (CategoryTagKeyGeneratorMixin,
                                        ResultsGenerator)
from trojsten.results.representation import ResultsTag, ResultsCell, ResultsCol
from trojsten.submit.models import Submit
from .default import CompetitionRules
from .default import FinishedRoundsResultsRulesMixin as FinishedRounds

KMS_ALFA = 'alfa'
KMS_BETA = 'beta'


KMS_ALFA_MAX_COEFFICIENT = 3
KMS_MAX_COEFFICIENTS = [0, 1, 2, 3, 4, 7, 100, 100, 100, 100, 100]
KMS_COEFFICIENT_PROP_NAME = 'KMS koeficient'


class KMSResultsGenerator(CategoryTagKeyGeneratorMixin,
                          ResultsGenerator):
    @staticmethod
    def get_user_coefficient(user):
        # As the user properties are prefetched, it is faster to find KMS coefficient in Python
        # than it would be by using `filter`, which would generate new query for each user
        coefficient_prop = [prop for prop in list(user.properties.all())
                            if prop.key.key_name == KMS_COEFFICIENT_PROP_NAME]
        return int(coefficient_prop[0].value) if coefficient_prop else 0

    def run(self, res_request):
        res_request.has_submit_in_beta = set()
        for submit in Submit.objects.filter(task__round__semester=res_request.round.semester,
                                            task__number__in=[8, 9, 10]).select_related('user'):
            res_request.has_submit_in_beta.add(submit.user)
        return super(KMSResultsGenerator, self).run(res_request)

    def is_user_active(self, request, user):
        active = super(KMSResultsGenerator, self).is_user_active(request, user)
        coefficient = self.get_user_coefficient(user)

        if self.tag.key == KMS_ALFA:
            # @FIXME This is a temporary hack, while the data to calculate whether
            # a user can solve this category or not are not available.
            # The data will be available once the old users are migrated.
            active = active and (coefficient <= KMS_ALFA_MAX_COEFFICIENT)

        if self.tag.key == KMS_BETA:
            active = active and \
                (coefficient > KMS_ALFA_MAX_COEFFICIENT or user in request.has_submit_in_beta)

        return active

    def deactivate_row_cells(self, request, row, cols):
        coefficient = self.get_user_coefficient(row.user)

        # Count only tasks your coefficient is eligible for
        for key in row.cells_by_key:
            if KMS_MAX_COEFFICIENTS[key] < coefficient:
                row.cells_by_key[key].active = False

        # Count only the best 5 tasks
        for excess in sorted((row.cells_by_key[key] for key in row.cells_by_key if row.cells_by_key[key].active),
                             key=lambda cell: -self.get_cell_total(request, cell))[5:]:
            excess.active = False

    def add_special_row_cells(self, res_request, row, cols):
        super(KMSResultsGenerator, self).add_special_row_cells(res_request, row, cols)
        coefficient = self.get_user_coefficient(row.user)
        row.cells_by_key[COEFFICIENT_COLUMN_KEY] = ResultsCell(str(coefficient))

    def create_results_cols(self, res_request):
        yield ResultsCol(key=COEFFICIENT_COLUMN_KEY, name='K.')
        for col in super(KMSResultsGenerator, self).create_results_cols(res_request):
            yield col


class KMSRules(FinishedRounds, CompetitionRules):

    RESULTS_TAGS = {
        KMS_ALFA: ResultsTag(key=KMS_ALFA, name='Alfa'),
        KMS_BETA: ResultsTag(key=KMS_BETA, name='Beta'),
    }

    RESULTS_GENERATOR_CLASS = KMSResultsGenerator
