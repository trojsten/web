from trojsten.results.generator import PrimarySchoolGeneratorMixin, ResultsGenerator

from .default import CompetitionRules


class PraskResultsGenerator(PrimarySchoolGeneratorMixin, ResultsGenerator):
    def get_minimal_year_of_graduation(self, res_request, user):
        return super().get_minimal_year_of_graduation(res_request, user) - 1


class PraskRules(CompetitionRules):

    RESULTS_GENERATOR_CLASS = PraskResultsGenerator
