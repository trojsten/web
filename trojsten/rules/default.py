# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone

from trojsten.contests.models import Round
from trojsten.results.constants import DEFAULT_TAG_KEY
from trojsten.results.generator import ResultsGenerator
from trojsten.results.representation import ResultsTag
from trojsten.submit import constants as submit_constants


class CompetitionRules(object):

    RESULTS_TAGS = {
        DEFAULT_TAG_KEY: ResultsTag(key=DEFAULT_TAG_KEY, name='')
    }

    RESULTS_GENERATOR_CLASS = ResultsGenerator

    def get_Q_for_graded_submits(self):
        return (
            models.Q(time__lte=models.F('task__round__end_time')) |
            models.Q(testing_status=submit_constants.SUBMIT_STATUS_REVIEWED)
        )

    def get_results_tags(self):
        return (self.RESULTS_TAGS[tag_key] for tag_key in self.RESULTS_TAGS)

    def get_results_generator(self, tag_key):
        if tag_key in self.RESULTS_TAGS:
            return self.RESULTS_GENERATOR_CLASS(tag=self.RESULTS_TAGS[tag_key])
        raise KeyError(tag_key)

    def get_previous_round(self, round):
        qs = round.series.round_set.filter(number=round.number - 1)
        if qs:
            return qs.get()
        else:
            return None

    def get_actual_result_rounds(self, competition):
        rounds = Round.objects.filter(series__competition=competition, visible=True)
        return rounds.order_by('-end_time', '-number')[:1]


class FinishedRoundsResultsRulesMixin():

    def get_actual_result_rounds(self, competition):
        rounds = Round.objects.filter(series__competition=competition, end_time__lte=timezone.now())
        return rounds.order_by('-end_time', '-number')[:1]
