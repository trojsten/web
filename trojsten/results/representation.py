# -*- coding: utf-8 -*-

from collections import namedtuple
from trojsten.utils.utils import Serializable

ResultsTag = namedtuple('ResultsTag', ['key', 'name'])


class ResultsCell(Serializable):

    def __init__(self, points=None, manual_points=None, auto_points=None, active=True):
        self.points = points
        self.manual_points = manual_points
        self.auto_points = auto_points
        self.active = active


class ResultsCol(Serializable):

    def __init__(self, key=None, name=None, task=None):
        self.key = key
        self.name = name
        self.task = task

    def encode(self):
        col_data = {
            'name': self.name,
            'key': self.key,
        }
        if (self.task is not None):
            col_data['task'] = dict(id=self.task.id, name=self.task.name)
        return col_data


class ResultsRow(Serializable):

    def __init__(
        self, user=None, school=None, name=None, year=None, school_name=None,
        previous=None, active=True
    ):
        if user is not None:
            school = school or user.school
            name = name or user.get_full_name()
            year = year if year is not None else user.school_year

        if school is not None:
            school_name = school_name or school.abbreviation or school.verbose_name

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
        self.cell_list = None

    def _calculate_cell_list(self, cols):
        self.cell_list = [self.cells_by_key[col.key] for col in cols]

    def _serialize_user_data(self):
        return {
            'id': self.user.id,
            'name': self.user.get_full_name(),
            'school': self._serialize_school_data(),
            'year': self.user.school_year,
        }

    def _serialize_school_data(self):
        if self.school:
            return {
                'id': self.school.id,
                'name': self.school_name,
                'verbose_name': self.school.verbose_name,
            }
        else:
            return None

    def encode(self):
        return {
            'user': self._serialize_user_data(),
            'cell_list': self.cell_list,
            'rank': self.rank,
            'total': self.total,
            'total_round': self.total_round,
            'previous': self.previous,
            'active': self.active
        }


class Results(Serializable):

    def __init__(self, round, tag=None, single_round=True, has_previous=False):
        self.cols = []
        self.rows = []

        self.round = round
        self.tag = tag
        self.single_round = single_round
        self.has_previous = has_previous

    def calculate_cell_lists(self):
        for row in self.rows:
            row._calculate_cell_list(self.cols)

    def iterrows(self):
        return iter(self.rows)

    def encode(self):
        return {
            'cols': self.cols,
            'rows': self.rows,
        }


class ResultsRequest(object):

    def __init__(self, round, single_round=True, previous_rows=None):
        self.round = round
        self.single_round = single_round

        if previous_rows is None:
            previous_rows = tuple()
        self.previous_rows_dict = {
            row.user.pk: row for row in previous_rows if row.user is not None
        }

    def get_previous_row_for_user(self, user):
        return self.previous_rows_dict.get(user.pk, None)
