# -*- coding: utf-8 -*-

from collections import namedtuple

from django.db import models
from django.utils import timezone

from trojsten.contests.models import Round
from trojsten.results.constants import DEFAULT_TAG_KEY, MAX_DAYS_TO_SHOW_ROUND_IN_ACTUAL_RESULTS
from trojsten.results.generator import ResultsGenerator
from trojsten.results.representation import ResultsTag
from trojsten.submit import constants as submit_constants


class CompetitionRules(object):

    RESULTS_TAGS = {DEFAULT_TAG_KEY: ResultsTag(key=DEFAULT_TAG_KEY, name="")}

    RESULTS_GENERATOR_CLASS = ResultsGenerator

    def get_Q_for_graded_submits(self):
        return models.Q(time__lte=models.F("task__round__end_time")) | models.Q(
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED
        )

    def get_results_tags(self):
        return (self.RESULTS_TAGS[tag_key] for tag_key in self.RESULTS_TAGS)

    def get_results_generator(self, tag_key):
        if tag_key in self.RESULTS_TAGS:
            return self.RESULTS_GENERATOR_CLASS(tag=self.RESULTS_TAGS[tag_key])
        raise KeyError(tag_key)

    def get_previous_round(self, round):
        qs = round.semester.round_set.filter(number=round.number - 1)
        if qs:
            return qs.get()
        else:
            return None

    def get_actual_result_rounds(self, competition):
        rounds = Round.objects.filter(
            semester__competition=competition,
            visible=True,
            end_time__gte=timezone.now()
            - timezone.timedelta(days=MAX_DAYS_TO_SHOW_ROUND_IN_ACTUAL_RESULTS),
        )
        return rounds.order_by("-end_time", "-number")[:1]

    def grade_text_submit(self, task, user, submitted_text):
        Grading = namedtuple("Grading", ["response", "points"])
        solution = [solution.lower() for solution in task.text_submit_solution]
        if submitted_text in solution:
            response = submit_constants.SUBMIT_RESPONSE_OK
            points = task.description_points
        else:
            response = submit_constants.SUBMIT_RESPONSE_WA
            points = 0
        return Grading(response, points)


class FinishedRoundsResultsRulesMixin:
    def get_actual_result_rounds(self, competition):
        rounds = Round.objects.filter(
            semester__competition=competition, visible=True, end_time__lte=timezone.now()
        )
        return rounds.order_by("-end_time", "-number")[:1]
