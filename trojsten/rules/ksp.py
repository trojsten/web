# -*- coding: utf-8 -*-

from itertools import chain
from collections import OrderedDict

from django.db import models

from trojsten.contests.models import Task
import trojsten.results.constants as results_constants
import trojsten.submit.constants as submit_constants
from trojsten.results.generator import ResultsGenerator
from trojsten.results.representation import ResultsTag, ResultsCell, ResultsCol
from trojsten.rules.default import CompetitionRules
from trojsten.rules.models import KSPLevel
from trojsten.submit.models import Submit


KSP_ALL = 'KSP_ALL'
KSP_L1, KSP_L2, KSP_L3, KSP_L4 = 'KSP_L1', 'KSP_L2', 'KSP_L3', 'KSP_L4'


class KSPResultsGenerator(ResultsGenerator):
    def get_results_level(self, level_for_all):
        """Returns the level of current results table or 'level_for_all' in case of KSP_ALL table."""
        return level_for_all if self.tag.key == KSP_ALL else int(self.tag.key[-1])

    def get_task_queryset(self, res_request):
        """In KSP_LX results table, there are results for tasks X-8."""
        return Task.objects.filter(
            round=res_request.round,
            number__gte=self.get_results_level(level_for_all=1)
        ).order_by('number')

    def run(self, res_request):
        res_request.user_levels = KSPLevel.objects.for_users_in_semester_as_dict(res_request.round.semester.pk)
        return super(KSPResultsGenerator, self).run(res_request)

    def is_user_active(self, res_request, user):
        """Deactivate users with level higher than level of the results table."""
        # TODO: Maybe deactivate users we don't want to show based on their points / submits.
        # Do this after users' results evaluation but before rank computation: overload calculate_row_ranks?
        # It is much faster (2x) to deactivate them than to filter them in the start of the results computation,
        # since for filtering, also all submits would have to be processed.
        active = super(KSPResultsGenerator, self)
        maximum_eligible_user_level = self.get_results_level(level_for_all=4)
        levels_are_ok = (res_request.user_levels[user.pk] <= maximum_eligible_user_level)
        return active and levels_are_ok

    def get_submit_queryset(self, res_request):
        """Returns the queryset of Submits that should be included in the results."""
        submits = super(KSPResultsGenerator, self).get_submit_queryset(res_request).select_related('task__round')

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

    def deactivate_row_cells(self, res_request, row, cols):
        user_level = res_request.user_levels[row.user.pk]

        # Don't count tasks below your level
        for task_number in row.cells_by_key:
            if task_number < user_level:
                row.cells_by_key[task_number].active = False

        # Count only the best 5 tasks
        for excess in sorted((cell for cell in row.cells_by_key.values() if cell.active),
                             key=lambda cell: -self.get_cell_total(res_request, cell))[5:]:
            excess.active = False

    def add_special_row_cells(self, request, row, cols):
        """Add user level column to results table."""
        super(KSPResultsGenerator, self).add_special_row_cells(request, row, cols)
        user_level = request.user_levels[row.user.pk]
        row.cells_by_key[results_constants.LEVEL_COLUMN_KEY] = ResultsCell(str(user_level))

    def create_results_cols(self, res_request):
        yield ResultsCol(key=results_constants.LEVEL_COLUMN_KEY, name='L')
        for col in super(KSPResultsGenerator, self).create_results_cols(res_request):
            yield col


class KSPRules(CompetitionRules):

    RESULTS_TAGS = OrderedDict([
        (KSP_ALL, ResultsTag(key=KSP_ALL, name='')),
        (KSP_L1, ResultsTag(key=KSP_L1, name='L1')),
        (KSP_L2, ResultsTag(key=KSP_L2, name='L2')),
        (KSP_L3, ResultsTag(key=KSP_L3, name='L3')),
        (KSP_L4, ResultsTag(key=KSP_L4, name='L4'))
    ])

    RESULTS_GENERATOR_CLASS = KSPResultsGenerator
