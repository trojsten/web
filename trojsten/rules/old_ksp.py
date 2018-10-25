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
        submits = super(KSPResultsGenerator, self).get_submit_queryset(res_request).select_related('task__round')

        penalized_submits = []

        if res_request.round.second_end_time is not None:
            penalized_submits = Submit.objects.filter(
                task__in=self.get_task_queryset(res_request),
            ).filter(
                submit_type=submit_constants.SUBMIT_TYPE_SOURCE
            ).filter(
                models.Q(time__gte=models.F('task__round__end_time'))
                & models.Q(time__lte=models.F('task__round__second_end_time'))
            ).order_by(
                'user', 'task', '-time', '-id',
            ).distinct(
                'user', 'task',
            ).select_related('user', 'user__school', 'task', 'task__round')
        return chain(submits, penalized_submits)

    def source_submit_points(self, previous_points, submit):
        """
        For all submits in submit queryset, the function `add_submit_to_row` is called.
        Source points in KSP are computed from two submits, which demands this processing:
        - user receives all points for the last submit before `round.end_time`
        - for the last submit in the second phase of the round user can additionally receive
          max(0, (points in second phase - previous points) / 2) points
        """
        if submit.time < submit.task.round.end_time:
            return max(previous_points, submit.user_points, key=self._comp_cell_value)
        else:
            if self._comp_cell_value(previous_points) > submit.user_points:
                return previous_points
            if previous_points is None or previous_points is results_constants.UNKNOWN_POINTS_SYMBOL:
                previous_points = 0
            return previous_points + (submit.user_points - previous_points) / 2

    def add_submit_to_row(self, res_request, submit, row):
        if submit.submit_type == submit_constants.SUBMIT_TYPE_SOURCE:
            cell = row.cells_by_key[submit.task.number]
            cell.auto_points = self.source_submit_points(cell.auto_points, submit)
        else:
            super(KSPResultsGenerator, self).add_submit_to_row(res_request, submit, row)


class KSPRules(CompetitionRules):

    RESULTS_TAGS = {
        KSP_Z: ResultsTag(key=KSP_Z, name='Z'),
        KSP_O: ResultsTag(key=KSP_O, name='O'),
    }

    RESULTS_GENERATOR_CLASS = KSPResultsGenerator
