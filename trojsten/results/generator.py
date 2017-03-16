# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model

from trojsten.people.constants import (GRADUATION_SCHOOL_YEAR,
                                       SCHOOL_YEAR_END_MONTH)
from trojsten.submit import constants as submit_constants
from trojsten.submit.models import Submit
from trojsten.contests.models import Task

from . import constants as c
from .representation import Results, ResultsCell, ResultsCol, ResultsRow


class ResultsGenerator(object):
    """
    Set of functions that are sequentially called when generating the results.
    The structure of calls is designed in a way that it should be easy to
    override some functionality. However, you can also override whole `run`
    function.
    """

    def __init__(self, tag):
        self.tag = tag

    def run(self, res_request):
        """
        The main function of ResultsGenerator. Takes a ResultsRequest object
        and creates corresponding Results object.

        Can modify ResultsRequest, however, should not modify ResultsGenerator
        instance itself.
        """
        results = self.create_empty_results(res_request)
        self.add_rows_to_results(res_request, results)
        self.sort_results(res_request, results)
        self.calculate_row_ranks(res_request, results)
        return results

    def create_empty_results(self, res_request):
        """
        Creates and returns Results instance with columns but no rows.
        """
        results = Results(
            round=res_request.round,
            tag=self.tag,
            single_round=res_request.single_round,
            has_previous=bool(not res_request.single_round and res_request.previous_rows_dict)
        )
        results.cols = list(self.create_results_cols(res_request))
        return results

    def create_results_cols(self, res_request):
        """
        Creates ResultsCol instances for the table and returns them
        as iterable in the correct order.
        """
        if not res_request.single_round and res_request.previous_rows_dict:
            yield ResultsCol(key=c.PREVIOUS_POINTS_COLUMN_KEY, name=c.PREVIOUS_POINTS_COLUMN_NAME)

        for task in self.get_task_queryset(res_request):
            yield ResultsCol(
                key=task.number, name=str(task.number), task=task
            )

        yield ResultsCol(key=c.TOTAL_POINTS_COLUMN_KEY, name=c.TOTAL_POINTS_COLUMN_NAME)

    def get_task_queryset(self, res_request):
        """
        Returns queryset of Tasks that should be included in the table.
        """
        return Task.objects.filter(round=res_request.round).order_by('number')

    def add_rows_to_results(self, res_request, results):
        """
        Adds complete and formated ResultsRow instances to the
        Results instance. The rows are not sorted yet.
        """
        row_dict = {}

        for uid in res_request.previous_rows_dict:
            row_dict[uid] = self.create_row(
                res_request, res_request.previous_rows_dict[uid].user, results.cols
            )

        for submit in self.get_submit_queryset(res_request):
            if submit.user.pk not in row_dict:
                row_dict[submit.user.pk] = self.create_row(res_request, submit.user, results.cols)
            self.add_submit_to_row(res_request, submit, row_dict[submit.user.pk])

        results.rows = list(row_dict.values())

        for row in results.rows:
            self.completize_row(res_request, row, results.cols)

    def get_submit_queryset(self, res_request):
        """
        Returns the queryset of Submits that should be included in the results.
        """
        rules = res_request.round.semester.competition.rules

        return Submit.objects.filter(
            task__in=self.get_task_queryset(res_request),
        ).filter(
            # TODO: filter users here?
            user__in=get_user_model().objects.all()
        ).filter(
            rules.get_Q_for_graded_submits()
        ).order_by(
            'user', 'task', 'submit_type', '-time', '-id',
        ).distinct(
            'user', 'task', 'submit_type'
        ).select_related('user', 'user__school', 'task')

    def create_row(self, res_request, user, cols):
        """
        Creates and returns new ResultsRow instance for specified user.
        Instance should have no cells and be ready to process Submits
        when `add_submit_to_row` is called.
        """
        row = ResultsRow(
            user=user,
            year=user.school_year_at(res_request.round.end_time),
            previous=res_request.get_previous_row_for_user(user),
            active=self.is_user_active(res_request, user),
        )
        for col in cols:
            if col.task is not None:
                row.cells_by_key[col.key] = ResultsCell()
        return row

    def is_user_active(self, res_request, user):
        """
        Returns whether the user should be included to ranking.

        This should exclude users that do not satisfy basic requirements.
        Exclusion based on the tasks and score should be done in
        `deactive_row_cells`.
        """
        competition = res_request.round.semester.competition
        minimal_year = self.get_minimal_year_of_graduation(res_request, user)
        return (
            user.graduation >= minimal_year and
            not user.is_competition_ignored(competition) and
            user.is_valid_for_competition(competition)
        )

    def get_minimal_year_of_graduation(self, res_request, user):
        """
        Returns minimal year given user must graduate in to be active.
        """
        return res_request.round.end_time.year + int(
            res_request.round.end_time.month > SCHOOL_YEAR_END_MONTH
        )

    def add_submit_to_row(self, res_request, submit, row):
        """
        Processes given Submit object and sets appropriate points
        to the corresponding RowCell instance.

        Points may appear either as the auto or as the manual points
        depending on submit type. Points should be a nonnegative
        number, None (no points) or UNKNOWN_POINTS_SYMBOL (there
        is a submit, but it is not reviewed yet.)
        """
        cell = row.cells_by_key[submit.task.number]
        if submit.submit_type == submit_constants.SUBMIT_TYPE_DESCRIPTION:
            if submit.testing_status == submit_constants.SUBMIT_STATUS_REVIEWED:
                points = submit.user_points
            else:
                points = c.UNKNOWN_POINTS_SYMBOL
            cell.manual_points = max(cell.manual_points, points, key=self._comp_cell_value)
        else:
            cell.auto_points = max(cell.auto_points, submit.user_points, key=self._comp_cell_value)

    def _comp_cell_value(self, x):
        if x is None:
            return -2
        if x is c.UNKNOWN_POINTS_SYMBOL:
            return -1
        return x

    def completize_row(self, res_request, row, cols):
        """
        Called after all Submits are processed with `add_submit_to_row`.
        Should calculate all the row properties but rank, completize and
        format all row cells.
        """
        self.deactivate_row_cells(res_request, row, cols)
        self.calculate_row_round_total(res_request, row, cols)
        self.calculate_row_total(res_request, row, cols)
        self.format_row_cells(res_request, row, cols)
        self.add_special_row_cells(res_request, row, cols)

    def deactivate_row_cells(self, requset, row, cols):
        """
        Deactivates row cells that should not be included in the results.
        May also deactivate whole row.

        Supposes row contains only cells that represent tasks.
        """
        pass

    def calculate_row_round_total(self, res_request, row, cols):
        """
        Calculates and sets single round total points for row.

        Supposes row contains only cells that represent tasks.
        """
        row.round_total = sum(
            self.get_cell_total(res_request, cell)
            for cell in row.cells_by_key.values() if cell.active
        )

    def get_cell_total(self, res_request, cell):
        """
        Returns total amount of points for cell.
        """
        return sum(
            value
            for value in (cell.manual_points, cell.auto_points)
            if value not in [None, c.UNKNOWN_POINTS_SYMBOL]
        )

    def calculate_row_total(self, res_request, row, cols):
        """
        Calculates and sets overall total points for row.

        Normally uses previous row instance and round total.

        Supposes row contains only cells that represent tasks.
        """
        row.total = row.round_total
        if row.previous is not None:
            row.total += row.previous.total

    def format_row_cells(self, res_request, row, cols):
        """
        Formats values in all the task cells into strings,
        that should be showed in the final resuls.

        This should be called after `calculate_row_total`, so all the values
        are already processed and nothing else but ranks should be calculated.

        Supposes row contains only cells that represent tasks.
        """
        for cell in row.cells_by_key.values():
            self.format_row_cell(res_request, cell)

    def format_row_cell(self, res_request, cell):
        """
        Formats single task cell values into strings.
        """
        total = self.get_cell_total(res_request, cell)
        cell.auto_points = self._str_cell_value(cell.auto_points)
        cell.manual_points = self._str_cell_value(cell.manual_points)
        if cell.auto_points == c.UNKNOWN_POINTS_SYMBOL:
            if cell.manual_points is not None:
                cell.points = c.PARTLY_UNKNOWN_FORMAT % cell.manual_points
            else:
                cell.points = c.UNKNOWN_POINTS_SYMBOL
        elif cell.manual_points == c.UNKNOWN_POINTS_SYMBOL:
            if cell.auto_points is not None:
                cell.points = c.PARTLY_UNKNOWN_FORMAT % cell.auto_points
            else:
                cell.points = c.UNKNOWN_POINTS_SYMBOL
        elif cell.auto_points is not None or cell.manual_points is not None:
            cell.points = str(total)
        else:
            cell.points = ""

    def _str_cell_value(self, value):
        return str(value) if value is not None else None

    def add_special_row_cells(self, res_request, row, cols):
        """
        Adds formated (containg string values) cells that correspond to
        columns other than tasks (previous points, total, bonus, ...).

        This should be called after the task representing cells are processed
        and formated. Should be using values accumulated in the ResultsRow instance.
        """
        prev_total = row.previous.total if row.previous is not None else 0
        row.cells_by_key[c.PREVIOUS_POINTS_COLUMN_KEY] = ResultsCell(str(prev_total))
        row.cells_by_key[c.TOTAL_POINTS_COLUMN_KEY] = ResultsCell(str(row.total))

    def sort_results(self, res_request, results):
        """
        Sorts rows of Results instance.
        """
        results.rows.sort(key=self.get_sort_key)

    def get_sort_key(self, row):
        """
        Returns the comparsion value of rows, that is used in sorting and
        rank calculation.
        """
        return -row.total

    def calculate_row_ranks(self, res_request, results):
        """
        Adds rank information to the ResultsRow instances based on their
        order in the Results object.
        """
        actual_rank = None
        next_rank = 1
        last_key = None
        for row in results.rows:

            if not row.active:
                row.rank = None
                continue

            actual_key = self.get_sort_key(row)
            if actual_key != last_key:
                actual_rank = next_rank
                last_key = actual_key
            next_rank += 1
            row.rank = actual_rank


class BonusColumnGeneratorMixin(object):

    def create_results_cols(self, res_request):
        if not res_request.single_round and res_request.previous_rows_dict:
            yield ResultsCol(key=c.PREVIOUS_POINTS_COLUMN_KEY, name=c.PREVIOUS_POINTS_COLUMN_NAME)

        for task in self.get_task_queryset(res_request):
            yield ResultsCol(
                key=task.number, name=str(task.number), task=task
            )

        yield ResultsCol(key=c.BONUS_POINTS_COLUMN_KEY, name=c.BONUS_POINTS_COLUMN_NAME)
        yield ResultsCol(key=c.TOTAL_POINTS_COLUMN_KEY, name=c.TOTAL_POINTS_COLUMN_NAME)

    def add_special_row_cells(self, res_request, row, cols):
        prev_total = row.previous.total if row.previous is not None else 0
        row.cells_by_key[c.PREVIOUS_POINTS_COLUMN_KEY] = ResultsCell(str(prev_total))
        row.cells_by_key[c.TOTAL_POINTS_COLUMN_KEY] = ResultsCell(str(row.total))
        row.cells_by_key[c.BONUS_POINTS_COLUMN_KEY] = ResultsCell(str(self.bonus))


class PrimarySchoolGeneratorMixin(object):

    def get_minimal_year_of_graduation(self, res_request, user):
        return res_request.round.end_time.year + GRADUATION_SCHOOL_YEAR + int(
            res_request.round.end_time.month > SCHOOL_YEAR_END_MONTH
        )


class CategoryTagKeyGeneratorMixin(object):

    def get_task_queryset(self, res_request):
        return Task.objects.filter(
            round=res_request.round,
            categories__name=self.tag.key,
        ).order_by('number')
