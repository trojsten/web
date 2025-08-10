# -*- coding: utf-8 -*-

from collections import OrderedDict

from trojsten.contests.models import Task
from trojsten.results.constants import LEVEL_COLUMN_KEY
from trojsten.results.generator import ResultsGenerator
from trojsten.results.representation import ResultsCell, ResultsCol, ResultsTag
from trojsten.rules.models import KMSLevel

from .default import CompetitionRules
from .default import FinishedRoundsResultsRulesMixin as FinishedRounds

KMS_L1 = "KMS_L1"
KMS_L2 = "KMS_L2"
KMS_L3 = "KMS_L3"
KMS_L4 = "KMS_L4"
KMS_L5 = "KMS_L5"

KMS_MO_FINALS_TYPE = "CKMO"
KMS_MO_REGIONALS_TYPE = "KKMO"


class KMSResultsGenerator(ResultsGenerator):
    def get_results_level(self):
        """Returns the level of current results table."""
        return int(self.tag.key[-1])

    def get_task_queryset(self, res_request):
        """Level X starts with task X, first three levels end at task 8"""
        level = self.get_results_level()
        tasks = Task.objects.filter(
            round=res_request.round, number__gte=self.get_results_level()
        ).order_by("number")
        if level <= 3:
            tasks = tasks.filter(number__lte=8)
        return tasks

    def run(self, res_request):
        res_request.user_levels = KMSLevel.objects.for_users_in_semester_as_dict(
            res_request.round.semester.pk
        )
        return super(KMSResultsGenerator, self).run(res_request)

    def is_user_active(self, res_request, user):
        """Deactivate users with level higher than level of the results table."""
        active = super(KMSResultsGenerator, self).is_user_active(res_request, user)
        return active and (res_request.user_levels[user.pk] <= self.get_results_level())

    def deactivate_row_cells(self, res_request, row, cols):
        user_level = res_request.user_levels[row.user.pk]

        # Don't count tasks below your level
        for task_number in row.cells_by_key:
            if task_number < user_level:
                row.cells_by_key[task_number].active = False

        # Count only the best 5 tasks
        for excess in sorted(
            (cell for cell in row.cells_by_key.values() if cell.active),
            key=lambda cell: -self.get_cell_total(res_request, cell),
        )[5:]:
            excess.active = False

    def add_special_row_cells(self, request, row, cols):
        """Add user level column to results table."""
        super(KMSResultsGenerator, self).add_special_row_cells(request, row, cols)
        user_level = request.user_levels[row.user.pk]
        row.cells_by_key[LEVEL_COLUMN_KEY] = ResultsCell(str(user_level))

    def create_results_cols(self, res_request):
        yield ResultsCol(key=LEVEL_COLUMN_KEY, name="Level")
        for col in super(KMSResultsGenerator, self).create_results_cols(res_request):
            yield col


class KMSRules(FinishedRounds, CompetitionRules):
    RESULTS_TAGS = OrderedDict(
        [
            (KMS_L1, ResultsTag(key=KMS_L1, name="L1")),
            (KMS_L2, ResultsTag(key=KMS_L2, name="L2")),
            (KMS_L3, ResultsTag(key=KMS_L3, name="L3")),
            (KMS_L4, ResultsTag(key=KMS_L4, name="L4")),
            (KMS_L5, ResultsTag(key=KMS_L5, name="L5")),
        ]
    )

    RESULTS_GENERATOR_CLASS = KMSResultsGenerator
