# -*- coding: utf-8 -*-

from itertools import chain
from collections import OrderedDict

from django.db import models

from trojsten.contests.models import Task
from trojsten.people.models import User
import trojsten.results.constants as results_constants
import trojsten.submit.constants as submit_constants
from trojsten.results.generator import ResultsGenerator
from trojsten.results.representation import ResultsTag, ResultsCell, ResultsCol
from trojsten.submit.models import Submit


from .default import CompetitionRules
from .ksp_levels import get_users_levels_for_semester

KSP_ALL = 'all'
KSP_L1, KSP_L2, KSP_L3, KSP_L4 = '1', '2', '3', '4'


class KSPResultsGenerator(ResultsGenerator):
    def get_task_queryset(self, res_request):
        return Task.objects.filter(
            round=res_request.round,
            number__gte=1 if self.tag.key == KSP_ALL else int(self.tag.key),
        ).order_by('number')

    def run(self, res_request):
        res_request.user_levels = get_users_levels_for_semester(User.objects.all(), res_request.round.semester)
        res_request.users = self.select_users(res_request)
        return super(KSPResultsGenerator, self).run(res_request)

    def select_users(self, res_request):
        users_with_submit_in_this_level = set()
        for submit in Submit.objects.select_related('user').filter(
                task__round__semester=res_request.round.semester,
                task__number__gte=1 if self.tag.key == KSP_ALL else int(self.tag.key) + 4):
            users_with_submit_in_this_level.add(submit.user)

        users = []
        results_level = 1 if self.tag.key == KSP_ALL else int(self.tag.key)
        for user, level in res_request.user_levels.items():
            if results_level == level or (results_level > level and user in users_with_submit_in_this_level):
                users.append(user)
        return users

    def get_submit_queryset(self, res_request):
        """
        Returns the queryset of Submits that should be included in the results.
        """
        submits = super(KSPResultsGenerator, self).get_submit_queryset(res_request)
        submits = submits.filter(user__in=res_request.users).select_related('task__round')

        penalized_submits = []

        if res_request.round.second_end_time is not None:
            penalized_submits = Submit.objects.filter(
                task__in=self.get_task_queryset(res_request),
            ).filter(
                user__in=res_request.users
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

    def deactivate_row_cells(self, request, row, cols):
        user_level = request.user_levels[row.user]

        # Don't count tasks below your level
        for key in row.cells_by_key:
            if key < user_level:
                row.cells_by_key[key].active = False

        # Count only the best 5 tasks
        for excess in sorted((row.cells_by_key[key] for key in row.cells_by_key if row.cells_by_key[key].active),
                             key=lambda cell: -self.get_cell_total(request, cell))[5:]:
            excess.active = False

    def add_special_row_cells(self, request, row, cols):
        super(KSPResultsGenerator, self).add_special_row_cells(request, row, cols)
        user_level = request.user_levels[row.user]
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
