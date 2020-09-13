# -*- coding: utf-8 -*-

from collections import namedtuple

from django.db.models import Count, Q
from django.utils import timezone

from trojsten.contests.models import Round
from trojsten.events.models import EventParticipant
from trojsten.people.models import UserPropertyKey
from trojsten.results.constants import (
    COEFFICIENT_COLUMN_KEY,
    MAX_DAYS_TO_SHOW_ROUND_IN_ACTUAL_RESULTS,
)
from trojsten.results.generator import CategoryTagKeyGeneratorMixin, ResultsGenerator
from trojsten.results.representation import ResultsCell, ResultsCol, ResultsTag
from trojsten.rules.susi_constants import *
from trojsten.submit.models import Submit

from .default import CompetitionRules


class SUSIResultsGenerator(CategoryTagKeyGeneratorMixin, ResultsGenerator):
    def __init__(self, tag):
        super(SUSIResultsGenerator, self).__init__(tag)
        self.susi_camps = None
        self.trojsten_camps = None
        self.puzzlehunt_participations_key = None
        self.coefficients = {}

    def get_user_coefficient(self, user, round):
        if user not in self.coefficients:
            if not self.susi_camps:
                self.prepare_coefficients(round)

            successful_semesters = self.susi_camps.get(user.pk, 0)
            puzzlehunt_participations = int(
                user.get_properties()[self.puzzlehunt_participations_key]
            )
            trojsten_camps = self.trojsten_camps.get(user.pk, 0)
            self.coefficients[user] = (
                5 * successful_semesters + 3 * puzzlehunt_participations + trojsten_camps
            )

        return self.coefficients[user]

    def get_graduation_status(self, user, res_request):
        minimal_year = super(SUSIResultsGenerator, self).get_minimal_year_of_graduation(
            res_request, user
        )
        return user.graduation < minimal_year

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
                    event__end_time__lt=round.semester.start_time,
                    event__end_time__year__gte=round.end_time.year - SUSI_YEARS_OF_CAMPS_HISTORY,
                ),
                Q(going=True),
            )
            .exclude(Q(event__type__name=SUSI_CAMP_TYPE))
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
                    event__end_time__lt=round.semester.start_time,
                    event__end_time__year__gte=round.end_time.year - SUSI_YEARS_OF_CAMPS_HISTORY,
                ),
                Q(going=True) | Q(type=EventParticipant.PARTICIPANT),
            )
            .values("user")
            .annotate(camps=Count("event__semester", distinct=True))
            .values_list("user", "camps")
        )

        self.puzzlehunt_participations_key = UserPropertyKey.objects.get(
            key_name=PUZZLEHUNT_PARTICIPATIONS_KEY_NAME
        )

    def run(self, res_request):
        self.prepare_coefficients(res_request.round)
        res_request.has_submit_in_blyskavica = set()
        for submit in (
            Submit.objects.filter(
                task__round__semester=res_request.round.semester,
                task__categories__name=SUSI_BLYSKAVICA,
            )
            .exclude(task__categories__name=SUSI_AGAT)
            .select_related("user")
        ):
            res_request.has_submit_in_blyskavica.add(submit.user)
        return super(SUSIResultsGenerator, self).run(res_request)

    def get_minimal_year_of_graduation(self, res_request, user):
        return -1

    def is_user_active(self, request, user):
        active = super(SUSIResultsGenerator, self).is_user_active(request, user)
        coefficient = self.get_user_coefficient(user, request.round)

        if self.tag.key == SUSI_AGAT:
            active = active and (
                (coefficient <= SUSI_AGAT_MAX_COEFFICIENT)
                and not self.get_graduation_status(user, request)
            )

        if self.tag.key == SUSI_BLYSKAVICA:
            active = active and (
                (
                    coefficient > SUSI_AGAT_MAX_COEFFICIENT
                    or user in request.has_submit_in_blyskavica
                )
                and not (self.get_graduation_status(user, request))
            )

        if self.tag.key == SUSI_CIFERSKY_CECH:
            active = active

        return active

    def deactivate_row_cells(self, request, row, cols):
        coefficient = self.get_user_coefficient(row.user, request.round)

        # Count only tasks your coefficient is eligible for, ignoring category Cifersky-cech
        for key in row.cells_by_key:
            if SUSI_ELIGIBLE_FOR_TASK_BOUND[key] < coefficient and not self.get_graduation_status(
                row.user, request
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


class SUSIRules(CompetitionRules):

    RESULTS_TAGS = {
        SUSI_CIFERSKY_CECH: ResultsTag(key=SUSI_CIFERSKY_CECH, name=SUSI_CIFERSKY_CECH),
        SUSI_AGAT: ResultsTag(key=SUSI_AGAT, name=SUSI_AGAT),
        SUSI_BLYSKAVICA: ResultsTag(key=SUSI_BLYSKAVICA, name=SUSI_BLYSKAVICA),
    }

    RESULTS_GENERATOR_CLASS = SUSIResultsGenerator

    def get_actual_result_rounds(self, competition):
        rounds = Round.objects.filter(
            semester__competition=competition,
            visible=True,
            end_time__gte=timezone.now()
            - timezone.timedelta(days=MAX_DAYS_TO_SHOW_ROUND_IN_ACTUAL_RESULTS),
        ).exclude(number=100, end_time__gte=timezone.now())
        return rounds.order_by("-end_time", "-number")[:1]

    def get_previous_round(self, round):
        previous_number = min(round.number - 1, 2)
        qs = round.semester.round_set.filter(number=previous_number)
        if qs:
            return qs.get()
        else:
            return None

    def grade_text_submit(self, task, user, submitted_text):
        now = timezone.now()
        Grading = namedtuple("Grading", ["response", "points"])
        solution = task.text_submit_solution[0].lower()
        if solution == submitted_text:
            response = "OK"
            points = SUSI_POINTS_ALLOCATION[0]
            if (
                task.round.susi_small_hint_date < now <= task.round.susi_big_hint_date
                and len(task.susi_small_hint) > 0
            ):
                points -= SUSI_POINTS_ALLOCATION[1]
            elif (
                task.round.susi_big_hint_date < now <= task.round.end_time
                and len(task.susi_big_hint) > 0
            ):
                points -= SUSI_POINTS_ALLOCATION[2]
            elif now > task.round.end_time:
                points = SUSI_POINTS_ALLOCATION[3]
        else:
            response = "WA"
            points = SUSI_POINTS_ALLOCATION[3]

        wrong_submits = len(
            Submit.objects.filter(task=task, user=user, time__lte=task.round.end_time).exclude(
                text=solution
            )
        )

        points = max(points - wrong_submits // SUSI_WRONG_SUBMITS_TO_PENALTY, 0)

        return Grading(response, points)
