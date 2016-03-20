from trojsten.results.generator import (CategoryTagKeyGeneratorMixin,
                                        ResultsGenerator)
from trojsten.results.representation import ResultsTag

from .default import CompetitionRules


class KSPResultsGenerator(CategoryTagKeyGeneratorMixin, ResultsGenerator):

    def is_user_active(self, request, user):
        active = super(KSPResultsGenerator, self).is_user_active(request, user)
        if self.tag.key == 'Z':
            active = active and True  # @TODO implement this condition
        return active


class KSPRules(CompetitionRules):

    RESULTS_TAGS = {
        'Z': ResultsTag(key='Z', name='Z'),
        'O': ResultsTag(key='O', name='O'),
    }

    RESULTS_GENERATOR_CLASS = KSPResultsGenerator
