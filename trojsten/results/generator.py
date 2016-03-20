# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.db import models

from trojsten.regal.people.constants import (GRADUATION_SCHOOL_YEAR,
                                             SCHOOL_YEAR_END_MONTH)
from trojsten.regal.tasks.models import Submit, Task
from trojsten.submit.constants import SUBMIT_STATUS_REVIEWED

from .representation import Results, ResultsCell, ResultsCol, ResultsRow


class ResultsGenerator(object):
    """
    Set of functions that are sequentially called when generating the results.
    The structure of calls is designed in a way that it should be easy to
    override some functionality. However, you can also override whole `run`
    function.

    Function call tree is following:
      - run
        - create_empty_results
          - create_results_cols
            - get_task_queryset
        - add_rows_to_results
          - get_submit_queryset
            - get_task_queryset
          - create_row
            - is_user_active
          - add_submit_to_row
          - completize_row
            - deactivate_row_cells
            - calculate_row_round_total
              - get_cell_total
            - calculate_row_total
            - format_row_cells
              - format_row_cell
            - add_special_row_cells
        - sort_results
          - get_sort_key
        - calculate_row_ranks
          - get_sort_key
    """

    UNKNOWN_POINTS_SYMBOL = '?'
    PARTLY_UNKNOWN_FORMAT = '%s?'

    def __init__(self, tag):
        self.tag = tag

    def run(self, request):
        """
        The main function of ResultsGenerator. Takes a ResultsRequest object
        and creates corresponding Results object.

        Can modify ResultsRequest, however, should not modify ResultsGenerator
        instance itself.
        """
        results = self.create_empty_results(request)
        self.add_rows_to_results(request, results)
        self.sort_results(request, results)
        self.calculate_row_ranks(request, results)
        return results

    def create_empty_results(self, request):
        """
        Creates and returns Results instance with columns but no rows.
        """
        results = Results(
            round=request.round,
            tag=self.tag,
            single_round=request.single_round,
        )
        results.cols = list(self.create_results_cols(request))
        return results

    def create_results_cols(self, request):
        """
        Creates ResultsCol instances for the table and returns them
        as iterable in the correct order.
        """
        if not request.single_round:
            yield ResultsCol(key='prev', name='P')

        for task in self.get_task_queryset(request):
            yield ResultsCol(
                key=task.number, name=str(task.number), task=task
            )

        yield ResultsCol(key='sum', name=u'∑')

    def get_task_queryset(self, request):
        """
        Returns queryset of Tasks that should be included in the table.
        """
        return Task.objects.filter(round=request.round)

    def add_rows_to_results(self, request, results):
        """
        Adds complete and formated ResultsRow instances to the
        Results instance. The rows are not sorted yet.
        """
        row_dict = {}

        for uid in request.previous_rows_dict:
            row_dict[uid] = self.create_row(
                request, request.previous_rows_dict[uid].user, results.cols
            )

        for submit in self.get_submit_queryset(request):
            if submit.user.pk not in row_dict:
                row_dict[submit.user.pk] = self.create_row(request, submit.user, results.cols)
            self.add_submit_to_row(request, submit, row_dict[submit.user.pk])

        results.rows = [row_dict[uid] for uid in row_dict]

        for row in results.rows:
            self.completize_row(request, row, results.cols)

    def get_submit_queryset(self, request):
        """
        Returns the queryset of Submits that should be included in the results.
        """
        rules = request.round.series.competition.rules

        return Submit.objects.filter(
            task__in=self.get_task_queryset(request),
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

    def create_row(self, request, user, cols):
        """
        Creates and returns new ResultsRow instance for specified user.
        Instance should have no cells and be ready to process Submits
        when `add_submit_to_row` is called.
        """
        row = ResultsRow(
            user=user,
            year=user.school_year_at(request.round.end_time),
            previous=request.get_previous_row_for_user(user),
            active=self.is_user_active(request, user),
        )
        for col in cols:
            if col.task is not None:
                row.cells_by_key[col.key] = ResultsCell()
        return row

    def is_user_active(self, request, user):
        """
        Returns whether the user should be included to ranking.

        This should exclude users that do not satisfy basic requirements.
        Exclusion based on the tasks and score should be done in
        `deactive_row_cells`.
        """
        minimal_year = self.get_minimal_year_of_graduation(request, user)
        return user.graduation >= minimal_year

    def get_minimal_year_of_graduation(self, request, user):
        """
        Returns minimal year given user must graduate in to be active.
        """
        return request.round.end_time.year + int(
            request.round.end_time.month > SCHOOL_YEAR_END_MONTH
        )

    def add_submit_to_row(self, request, submit, row):
        """
        Processes given Submit object and sets appropriate points
        to the corresponding RowCell instance.

        Points may appear either as the auto or as the manual points
        depending on submit type. Points should be a nonnegative
        number, None (no points) or UNKNOWN_POINTS_SYMBOL (there
        is a submit, but it is not reviewed yet.)
        """
        cell = row.cells_by_key[submit.task.number]
        if submit.submit_type == Submit.DESCRIPTION:
            if submit.testing_status == SUBMIT_STATUS_REVIEWED:
                points = submit.points
            else:
                points = self.UNKNOWN_POINTS_SYMBOL
            cell.manual_points = max(cell.manual_points, points, key=self._comp_cell_value)
        else:
            cell.auto_points = max(cell.auto_points, submit.points, key=self._comp_cell_value)

    def _comp_cell_value(self, x):
        if x is None:
            return -2
        if x is self.UNKNOWN_POINTS_SYMBOL:
            return -1
        return x

    def completize_row(self, request, row, cols):
        """
        Called after all Submits are processed with `add_submit_to_row`.
        Should calculate all the row properties but rank, completize and
        format all row cells.
        """
        self.deactivate_row_cells(request, row, cols)
        self.calculate_row_round_total(request, row, cols)
        self.calculate_row_total(request, row, cols)
        self.format_row_cells(request, row, cols)
        self.add_special_row_cells(request, row, cols)

    def deactivate_row_cells(self, requset, row, cols):
        """
        Deactivates row cells that should not be included in the results.
        May also deactivate whole row.

        Supposes row contains only cells that represent tasks.
        """
        pass

    def calculate_row_round_total(self, request, row, cols):
        """
        Calculates and sets single round total points for row.

        Supposes row contains only cells that represent tasks.
        """
        row.round_total = sum(
            self.get_cell_total(request, cell)
            for cell in row.cells_by_key.values() if cell.active
        )

    def get_cell_total(self, request, cell):
        """
        Returns total amount of points for cell.
        """
        return sum(
            value
            for value in (cell.manual_points, cell.auto_points)
            if value not in [None, self.UNKNOWN_POINTS_SYMBOL]
        )

    def calculate_row_total(self, request, row, cols):
        """
        Calculates and sets overall total points for row.

        Normally uses previous row instance and round total.

        Supposes row contains only cells that represent tasks.
        """
        row.total = row.round_total
        if row.previous is not None:
            row.total += row.previous.total

    def format_row_cells(self, request, row, cols):
        """
        Formats values in all the task cells into strings,
        that should be showed in the final resuls.

        This should be called after `calculate_row_total`, so all the values
        are already processed and nothing else but ranks should be calculated.

        Supposes row contains only cells that represent tasks.
        """
        for cell in row.cells_by_key.values():
            self.format_row_cell(request, cell)

    def format_row_cell(self, request, cell):
        """
        Formats single task cell values into strings.
        """
        total = self.get_cell_total(request, cell)
        cell.auto_points = self._str_cell_value(cell.auto_points)
        cell.manual_points = self._str_cell_value(cell.manual_points)
        if cell.auto_points == self.UNKNOWN_POINTS_SYMBOL:
            cell.points = self.PARTLY_UNKNOWN_FORMAT % cell.manual_points
        elif cell.manual_points == self.UNKNOWN_POINTS_SYMBOL:
            cell.points = self.PARTLY_UNKNOWN_FORMAT % cell.auto_points
        else:
            cell.points = str(total)

    def _str_cell_value(self, value):
        return str(value) if value is not None else None

    def add_special_row_cells(self, request, row, cols):
        """
        Adds formated (containg string values) cells that correspond to
        columns other than tasks (previous points, total, bonus, ...).

        This should be called after the task representing cells are processed
        and formated. Should be using values accumulated in the ResultsRow instance.
        """
        prev_total = row.previous.total if row.previous is not None else 0
        row.cells_by_key['prev'] = ResultsCell(str(prev_total))
        row.cells_by_key['sum'] = ResultsCell(str(row.total))

    def sort_results(self, request, results):
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

    def calculate_row_ranks(self, request, results):
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

    def create_results_cols(self, request):
        if not request.single_round:
            yield ResultsCol(key='prev', name='P')

        for task in self.get_task_queryset(request):
            yield ResultsCol(
                key=task.number, name=str(task.number), task=task
            )

        yield ResultsCol(key='bonus', name='B')
        yield ResultsCol(key='sum', name=u'∑')


class PrimarySchoolGeneratorMixin(object):

    def get_minimal_year_of_graduation(self, request, user):
        return request.round.end_time.year + GRADUATION_SCHOOL_YEAR + int(
            request.round.end_time.month > SCHOOL_YEAR_END_MONTH
        )


class CategoryTagKeyGeneratorMixin(object):

    def get_task_queryset(self, request):
        return Task.objects.filter(
            round=request.round,
            category__name=self.tag.key,
        )
