# -*- coding: utf-8 -*-

from collections import namedtuple


class ResultsCell(object):

    def __init__(self, points=None, manual_points=None, auto_points=None, active=True):
        self.points=points
        self.manual_points=manual_points
        self.auto_points=auto_points
        self.active=active

class ResultsCol(object):

    def __init__(self, key=None, name=None, task=None):
        self.key=key
        self.name=name
        self.task=task

class ResultsRow(object):

    def __init__(
        self, user=None, school=None, name=None, year=None, school_name=None,
        previous=None, active=True
    ):
        if user is not None:
            school = school or user.school
            name = name or user.get_full_name()
            year = year if year is not None else user.school_year

        if school is not None:
            school_name = school_name or school.abbreviation

        self.cells_by_key = {}
        self.previous = previous
        self.active = active

        self.user = user
        self.school = school
        self.name = name
        self.school_name = school_name
        self.year = year

        self.total = 0
        self.total_round = 0
        self.rank = None

    def _calculate_cell_list(self, cols):
        self.cell_list = [self.cells_by_key[col.key] for col in cols]


class Results(object):

    def __init__(self, round, name='', single_round=True):
        self.cols = []
        self.rows = []

        self.round = round
        self.name = name
        self.single_round = single_round

    def calculate_cell_lists(self):
        for row in self.rows:
            row._calculate_cell_list(self.cols)

    def iterrows(self):
        return iter(self.rows)


class ResultsRequest(object):

    def __init__(self, round, single_round, previous_rows):
        self.round = round
        self.single_round = single_round

        if previous_rows is None:
            previous_rows = ()
        self.previous_rows_dict = {
            row.user.pk: row for row in previous_rows if row.user is not None
        }

    def get_previous_row_for_user(self, user):
        return self.previous_rows_dict.get(user.pk, None)
