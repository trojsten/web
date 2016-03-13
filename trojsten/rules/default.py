# -*- coding: utf-8 -*-

from django.db import models

from trojsten.results.generator import ResultsGenerator
from trojsten.submit import constants as submit_constants


class CompetitionRules(object):

    RESULTS_GENERATORS = {
        "": ResultsGenerator()
    }

    def get_Q_for_graded_submits(self):
        return (
            models.Q(time__lte=models.F('task__round__end_time'))
            | models.Q(testing_status=submit_constants.SUBMIT_STATUS_REVIEWED)
        )

    def get_results_generators(self):
        return self.RESULTS_GENERATORS

    def get_previous_round(self, round):
        qs = round.series.round_set.filter(number=round.number-1)
        if qs:
            return qs.get()
        else:
            return None
