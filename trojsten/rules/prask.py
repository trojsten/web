from trojsten.results.generator import PrimarySchoolGeneratorMixin, ResultsGenerator

from .default import CompetitionRules


class PraskResultsGenerator(PrimarySchoolGeneratorMixin, ResultsGenerator):
    pass


class PraskRules(CompetitionRules):

    RESULTS_GENERATOR_CLASS = PraskResultsGenerator
