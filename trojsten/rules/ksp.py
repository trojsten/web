from trojsten.results.generator import (CategoryTagKeyGeneratorMixin,
                                        ResultsGenerator)
from trojsten.results.representation import ResultsTag

from .default import CompetitionRules

KSP_Z = 'Z'
KSP_O = 'O'


class KSPResultsGenerator(CategoryTagKeyGeneratorMixin, ResultsGenerator):

    def is_user_active(self, request, user):
        active = super(KSPResultsGenerator, self).is_user_active(request, user)
        if self.tag.key == 'KSP_Z':
            active = active and True  # @TODO implement this condition
        return active


class KSPRules(CompetitionRules):

    RESULTS_TAGS = {
        KSP_Z: ResultsTag(key=KSP_Z, name='Z'),
        KSP_O: ResultsTag(key=KSP_O, name='O'),
    }

    RESULTS_GENERATOR_CLASS = KSPResultsGenerator
