# -*- coding: utf-8 -*-

from django.db.models import Count, Q

from trojsten.events.models import EventParticipant
from trojsten.results.constants import COEFFICIENT_COLUMN_KEY
from trojsten.results.generator import CategoryTagKeyGeneratorMixin, ResultsGenerator
from trojsten.results.representation import ResultsCell, ResultsCol, ResultsTag
from trojsten.submit.models import Submit

from .default import CompetitionRules
from .default import FinishedRoundsResultsRulesMixin as FinishedRounds

SUSI_ALEF = "alef"
SUSI_BET = "bet"
SUSI_GIMEL = "gimel"


SUSI_ALEF_MAX_COEFFICIENT = 8
SUSI_ELIGIBLE_FOR_TASK_BOUND = [8, 8, 1000, 1000, 1000, 1000, 1000]

SUSI_CAMP_TYPE = "SuŠi sústredenie"

SUSI_YEARS_OF_CAMPS_HISTORY = 10


class SUSIResultsGenerator(CategoryTagKeyGeneratorMixin, ResultsGenerator):
    def __init__(self, tag):
        super(SUSIResultsGenerator, self).__init__(tag)
        self.susi_camps = None
        self.trojsten_camps = None
        self.puzzlehunt_participations = None
        self.has_graduated = None
        self.coefficients = {}

    def get_user_coefficient(self, user, round):
        if user not in self.coefficients:
            if not self.susi_camps:
                self.prepare_coefficients(round)

            successful_semesters = self.susi_camps.get(user.pk, 0)
            puzzlehunt_participations = self.puzzlehunt_participations.get(user.pk, 0)
            trojsten_camps = self.trojsten_camps.get(user.pk, 0)
            self.coefficients[user] = (
                5 * successful_semesters + 3 * puzzlehunt_participations + trojsten_camps
            )

        return self.coefficients[user]

    def get_graduation_status(self, user, round):
        if user not in self.has_graduated:
            if not self.has_graduated:
                self.prepare_coefficients(round)

        return self.has_graduated[user]

    def prepare_coefficients(self, round):
        """
        Fetch from the db number of successful semester and number of participation
        in other Trojsten camps of each user and store them in dictionaries. The prepared
        data in dictionaries are used to compute the coefficient of a given user.
        We consider only events happened before given round, so the coefficients are computed
        correct in older results.
        """

        self.trojsten_camps = dict(
            EventParticipant.objects.filter(
                Q(
                    # TODO I think commenting next line will retrieve participations in all trojsten camps
                    # event__type__name=SUSI_CAMP_TYPE,
                    event__end_time__lt=round.end_time,
                    event__end_time__year__gte=round.end_time.year - SUSI_YEARS_OF_CAMPS_HISTORY,
                ),
                Q(going=True) | Q(type=EventParticipant.PARTICIPANT),
            )
            .values("user")
            .annotate(camps=Count("event__semester", distinct=True))
            .values_list("user", "camps")
        )

        # We ignore camps that happened before SUSI_YEARS_OF_CAMPS_HISTORY years, so we don't
        # produce too big dictionaries of users.
        self.susi_camps = dict(
            EventParticipant.objects.filter(
                Q(
                    event__type__name=SUSI_CAMP_TYPE,
                    event__end_time__lt=round.end_time,
                    event__end_time__year__gte=round.end_time.year - SUSI_YEARS_OF_CAMPS_HISTORY,
                ),
                Q(going=True) | Q(type=EventParticipant.PARTICIPANT),
            )
            .values("user")
            .annotate(camps=Count("event__semester", distinct=True))
            .values_list("user", "camps")
        )

        # TODO Fill dictionary with values of property "SUSI_Ucasti_na_sifrovackach" for all susi participants
        self.puzzlehunt_participations = None

        # TODO Fill dictionary with booleans, indicating whether a participant has ended high school or not
        self.has_graduated = None

    def run(self, res_request):
        self.prepare_coefficients(res_request.round)
        res_request.has_submit_in_bet = set()
        for submit in Submit.objects.filter(
            task__round__semester=res_request.round.semester, task__number__in=[6, 7]
        ).select_related("user"):
            res_request.has_submit_in_bet.add(submit.user)
        return super(SUSIResultsGenerator, self).run(res_request)

    def is_user_active(self, request, user):
        active = super(SUSIResultsGenerator, self).is_user_active(request, user)
        coefficient = self.get_user_coefficient(user, request.round)

        if self.tag.key == SUSI_ALEF:
            active = active and (
                (coefficient <= SUSI_ALEF_MAX_COEFFICIENT)
                and not self.get_graduation_status(user, request.round)
            )

        if self.tag.key == SUSI_BET:
            active = active and (
                (coefficient > SUSI_ALEF_MAX_COEFFICIENT or user in request.has_submit_in_bet)
                and not (self.get_graduation_status(user, request.round))
            )

        if self.tag.key == SUSI_GIMEL:
            active = active

        return active

    def deactivate_row_cells(self, request, row, cols):
        coefficient = self.get_user_coefficient(row.user, request.round)

        # Count only tasks your coefficient is eligible for, ignoring category Gimel
        for key in row.cells_by_key:
            if SUSI_ELIGIBLE_FOR_TASK_BOUND[key] < coefficient and not self.get_graduation_status(
                row.user, request.round
            ):
                row.cells_by_key[key].active = False

        # Prepare list of pairs consisting of cell and its points.
        tasks = [
            (cell, self.get_cell_total(request, cell))
            for key, cell in row.cells_by_key.items()
            if row.cells_by_key[key].active
        ]

        # Count only the best 5 tasks
        for cell, _ in sorted(tasks, key=lambda x: x[1])[:-5]:
            cell.active = False

    def calculate_row_round_total(self, res_request, row, cols):
        # coefficient = self.get_user_coefficient(row.user, res_request.round)

        row.round_total = sum(
            self.get_cell_total(res_request, cell)
            for key, cell in row.cells_by_key.items()
            if cell.active
        )

    def add_special_row_cells(self, res_request, row, cols):
        super(SUSIResultsGenerator, self).add_special_row_cells(res_request, row, cols)
        coefficient = self.get_user_coefficient(row.user, res_request.round)
        row.cells_by_key[COEFFICIENT_COLUMN_KEY] = ResultsCell(str(coefficient))

    def create_results_cols(self, res_request):
        yield ResultsCol(key=COEFFICIENT_COLUMN_KEY, name="B.S.")
        for col in super(SUSIResultsGenerator, self).create_results_cols(res_request):
            yield col


class SUSIRules(FinishedRounds, CompetitionRules):

    RESULTS_TAGS = {
        SUSI_ALEF: ResultsTag(key=SUSI_ALEF, name="Alef"),
        SUSI_BET: ResultsTag(key=SUSI_BET, name="Bet"),
        SUSI_GIMEL: ResultsTag(key=SUSI_GIMEL, name="Gimel"),
    }

    RESULTS_GENERATOR_CLASS = SUSIResultsGenerator
