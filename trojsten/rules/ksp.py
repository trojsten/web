from itertools import chain

from django.db import models

import trojsten.results.constants as results_constants
import trojsten.submit.constants as submit_constants
from trojsten.results.generator import (CategoryTagKeyGeneratorMixin,
                                        ResultsGenerator)
from trojsten.results.representation import ResultsTag
from trojsten.submit.models import Submit


from .default import CompetitionRules

KSP_Z = 'Z'
KSP_O = 'O'


class KSPResultsGenerator(CategoryTagKeyGeneratorMixin, ResultsGenerator):

    def is_user_active(self, request, user):
        active = super(KSPResultsGenerator, self).is_user_active(request, user)
        if self.tag.key == 'KSP_Z':
            active = active and True  # @TODO implement this condition
        return active

    def get_submit_queryset(self, res_request):
        """
        Returns the queryset of Submits that should be included in the results.
        """
        rules = res_request.round.semester.competition.rules

        submits = Submit.objects.filter(
            task__in=self.get_task_queryset(res_request),
        ).filter(
            rules.get_Q_for_graded_submits()
        ).order_by(
            'user', 'task', 'submit_type', '-time', '-id',
        ).distinct(
            'user', 'task', 'submit_type'
        ).select_related('user', 'user__school', 'task', 'task__round')

        penalized_submits = []

        if res_request.round.second_end_time is not None:
            penalized_submits = Submit.objects.filter(
                task__in=self.get_task_queryset(res_request),
            ).filter(
                submit_type=submit_constants.SUBMIT_TYPE_SOURCE
            ).filter(
                models.Q(time__gte=models.F('task__round__end_time')) &
                models.Q(time__lte=models.F('task__round__second_end_time'))
            ).order_by(
                'user', 'task', '-time', '-id',
            ).distinct(
                'user', 'task',
            ).select_related('user', 'user__school', 'task', 'task__round')
        return chain(submits, penalized_submits)

    def source_submit_points(self, previous_points, submit):
        if submit.time < submit.task.round.end_time:
            return max(previous_points, submit.user_points, key=self._comp_cell_value)
        else:
            if self._comp_cell_value(previous_points) > submit.user_points:
                return previous_points
            if previous_points is None or previous_points is results_constants.UNKNOWN_POINTS_SYMBOL:
                previous_points = 0
            return previous_points + (submit.user_points - previous_points) / 2

    def add_submit_to_row(self, res_request, submit, row):
        cell = row.cells_by_key[submit.task.number]
        if submit.submit_type == submit_constants.SUBMIT_TYPE_DESCRIPTION:
            if submit.testing_status == submit_constants.SUBMIT_STATUS_REVIEWED:
                points = submit.user_points
            else:
                points = results_constants.UNKNOWN_POINTS_SYMBOL
            cell.manual_points = max(cell.manual_points, points, key=self._comp_cell_value)
        elif submit.submit_type == submit_constants.SUBMIT_TYPE_SOURCE:
            cell.auto_points = self.source_submit_points(cell.auto_points, submit)
        else:
            cell.auto_points = max(cell.auto_points, submit.user_points, key=self._comp_cell_value)


class KSPRules(CompetitionRules):

    RESULTS_TAGS = {
        KSP_Z: ResultsTag(key=KSP_Z, name='Z'),
        KSP_O: ResultsTag(key=KSP_O, name='O'),
    }

    RESULTS_GENERATOR_CLASS = KSPResultsGenerator
