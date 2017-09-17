# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from django.db.models import Q, Count
from django.utils import timezone

from trojsten.events.models import EventParticipant
from trojsten.people.constants import SCHOOL_YEAR_END_MONTH
from trojsten.results.constants import COEFFICIENT_COLUMN_KEY
from trojsten.results.generator import (CategoryTagKeyGeneratorMixin,
                                        ResultsGenerator)
from trojsten.results.representation import ResultsTag, ResultsCell, ResultsCol
from trojsten.submit.models import Submit
from .default import CompetitionRules
from .default import FinishedRoundsResultsRulesMixin as FinishedRounds

KMS_ALFA = 'alfa'
KMS_BETA = 'beta'


KMS_ALFA_MAX_COEFFICIENT = 3
KMS_MAX_COEFFICIENTS = [0, 1, 2, 3, 4, 7, 100, 100, 100, 100, 100]

KMS_CAMP_TYPE = 'KMS sústredenie'
KMS_MO_FINALS_TYPE = 'CKMO'

KMS_YEARS_OF_CAMPS_HISTORY = 10


class KMSResultsGenerator(CategoryTagKeyGeneratorMixin,
                          ResultsGenerator):
    def __init__(self, tag):
        super(KMSResultsGenerator, self).__init__(tag)
        self.camps = None
        self.mo_finals = None

    def get_user_coefficient(self, user, round):
        if not self.camps or not self.mo_finals:
            self.prepare_coefficients(round)

        year = user.school_year_at(round.end_time)
        successful_semesters = self.camps.get(user.pk, 0)
        mo_finals = self.mo_finals.get(user.pk, 0)

        return year + (2 * successful_semesters - 1) // 3 + mo_finals + 1

    def prepare_coefficients(self, round):
        """
        Fetch from the db number of successful semester and number of participation
        in MO final for each user and store them in dictionaries. The prepared
        data in dictionaries are used to compute the coefficient of a given user.
        We consider only events happened before given round, so the coefficients are computed
        correct in older results.
        """
        # We count only MO finals in previous school years, the user coefficient remains the same
        # during a semester. We assume that the MO finals are held in the last semester
        # of a year.
        school_year = round.end_time.year - int(round.end_time.month < SCHOOL_YEAR_END_MONTH)
        prev_school_year_end =\
            timezone.make_aware(datetime.datetime(school_year, SCHOOL_YEAR_END_MONTH, 28))

        self.mo_finals = dict(EventParticipant.objects.filter(
            event__type__name=KMS_MO_FINALS_TYPE, event__end_time__lt=prev_school_year_end
        ).values('user').annotate(mo_finals=Count('event')).values_list('user', 'mo_finals'))
        # We ignore camps that happened before KMS_YEARS_OF_CAMPS_HISTORY years, so we don't
        # produce too big dictionaries of users.
        self.camps = dict(EventParticipant.objects.filter(
            Q(event__type__name=KMS_CAMP_TYPE, event__end_time__lt=round.end_time,
              event__end_time__year__gte=round.end_time.year - KMS_YEARS_OF_CAMPS_HISTORY),
            Q(going=True) | Q(type=EventParticipant.PARTICIPANT)
        ).values('user').annotate(camps=Count('event__semester', distinct=True))
                        .values_list('user', 'camps'))

    def run(self, res_request):
        self.prepare_coefficients(res_request.round)
        res_request.has_submit_in_beta = set()
        for submit in Submit.objects.filter(task__round__semester=res_request.round.semester,
                                            task__number__in=[8, 9, 10]).select_related('user'):
            res_request.has_submit_in_beta.add(submit.user)
        return super(KMSResultsGenerator, self).run(res_request)

    def is_user_active(self, request, user):
        active = super(KMSResultsGenerator, self).is_user_active(request, user)
        coefficient = self.get_user_coefficient(user, request.round)

        if self.tag.key == KMS_ALFA:
            active = active and (coefficient <= KMS_ALFA_MAX_COEFFICIENT)

        if self.tag.key == KMS_BETA:
            active = active and \
                (coefficient > KMS_ALFA_MAX_COEFFICIENT or user in request.has_submit_in_beta)

        return active

    def deactivate_row_cells(self, request, row, cols):
        coefficient = self.get_user_coefficient(row.user, request.round)

        # Count only tasks your coefficient is eligible for
        for key in row.cells_by_key:
            if KMS_MAX_COEFFICIENTS[key] < coefficient:
                row.cells_by_key[key].active = False

        # Count only the best 5 tasks
        for excess in sorted((row.cells_by_key[key] for key in row.cells_by_key if row.cells_by_key[key].active),
                             key=lambda cell: -self.get_cell_total(request, cell))[5:]:
            excess.active = False

    def add_special_row_cells(self, res_request, row, cols):
        super(KMSResultsGenerator, self).add_special_row_cells(res_request, row, cols)
        coefficient = self.get_user_coefficient(row.user, res_request.round)
        row.cells_by_key[COEFFICIENT_COLUMN_KEY] = ResultsCell(str(coefficient))

    def create_results_cols(self, res_request):
        yield ResultsCol(key=COEFFICIENT_COLUMN_KEY, name='K.')
        for col in super(KMSResultsGenerator, self).create_results_cols(res_request):
            yield col


class KMSRules(FinishedRounds, CompetitionRules):

    RESULTS_TAGS = {
        KMS_ALFA: ResultsTag(key=KMS_ALFA, name='Alfa'),
        KMS_BETA: ResultsTag(key=KMS_BETA, name='Beta'),
    }

    RESULTS_GENERATOR_CLASS = KMSResultsGenerator
