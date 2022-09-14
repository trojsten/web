# -*- coding: utf-8 -*-

from collections import namedtuple

from django.db.models import Count, Q
from django.utils import timezone
from unidecode import unidecode

import trojsten.rules.susi_constants as constants
from trojsten.contests.models import Round
from trojsten.events.models import EventParticipant
from trojsten.people.models import UserPropertyKey
from trojsten.results.constants import (
    COEFFICIENT_COLUMN_KEY,
    MAX_DAYS_TO_SHOW_ROUND_IN_ACTUAL_RESULTS,
)
from trojsten.results.generator import CategoryTagKeyGeneratorMixin, ResultsGenerator
from trojsten.results.representation import ResultsCell, ResultsCol, ResultsTag
from trojsten.submit.constants import SUBMIT_RESPONSE_OK, SUBMIT_RESPONSE_WA
from trojsten.submit.models import Submit

from .default import CompetitionRules
from .kms import KMS_MO_FINALS_TYPE


class SUSIResultsGenerator(CategoryTagKeyGeneratorMixin, ResultsGenerator):
    def __init__(self, tag):
        super(SUSIResultsGenerator, self).__init__(tag)
        self.susi_camps = None
        self.trojsten_camps = None
        self.successful_semesters = None
        self.puzzlehunt_participations_key = None
        self.coefficients = {}

    def get_user_coefficient(self, user, round):
        if user not in self.coefficients:
            if not self.susi_camps:
                self.prepare_coefficients(round)

            no_of_susi_camps = self.susi_camps.get(user.pk, 0)
            no_of_successful_semesters = self.successful_semesters.get(user.pk, 0)
            try:
                no_of_puzzlehunt_participations = int(
                    user.get_properties()[self.puzzlehunt_participations_key]
                )
            except KeyError:
                no_of_puzzlehunt_participations = 0
            no_of_trojsten_camps = self.trojsten_camps.get(user.pk, 0)
            self.coefficients[user] = (
                constants.SUSI_EXP_POINTS_FOR_SUSI_CAMP * no_of_susi_camps
                + constants.SUSI_EXP_POINTS_FOR_PUZZLEHUNT * no_of_puzzlehunt_participations
                + constants.SUSI_EXP_POINTS_FOR_SOLVED_TASKS * no_of_successful_semesters
                + constants.SUSI_EXP_POINTS_FOR_OTHER_CAMP * no_of_trojsten_camps
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
                event__end_time__lt=round.semester.start_time,
                event__end_time__year__gte=round.end_time.year
                - constants.SUSI_YEARS_OF_CAMPS_HISTORY,
                going=True,
            )
            .exclude(Q(event__type__name=constants.SUSI_CAMP_TYPE))
            .exclude(Q(event__type__name=KMS_MO_FINALS_TYPE))
            .values("user")
            .annotate(camps=Count("event__semester"))
            .values_list("user", "camps")
        )

        # We ignore camps that happened before SUSI_YEARS_OF_CAMPS_HISTORY years, so we don't
        # produce too big dictionaries of users.
        self.susi_camps = dict(
            EventParticipant.objects.filter(
                event__type__name=constants.SUSI_CAMP_TYPE,
                event__end_time__lt=round.semester.start_time,
                event__end_time__year__gte=round.end_time.year
                - constants.SUSI_YEARS_OF_CAMPS_HISTORY,
                going=True,
            )
            .exclude(type=EventParticipant.ORGANIZER)
            .values("user")
            .annotate(camps=Count("event__semester", distinct=True))
            .values_list("user", "camps")
        )

        self.successful_semesters = dict()
        no_of_solved_tasks_per_semester = list(
            Submit.objects.filter(
                Q(task__round__semester__competition=round.semester.competition, points__gt=0),
                Q(task__round__semester__year__lt=round.semester.year)
                | Q(
                    task__round__semester__year=round.semester.year,
                    task__round__semester__number__lt=round.semester.number,
                ),
            )
            .values("user", "task__round__semester")
            .annotate(solved_tasks=Count("task", distinct=True))
            .values_list("user", "solved_tasks")
        )

        for user_id, no_of_solved_tasks in no_of_solved_tasks_per_semester:
            if no_of_solved_tasks >= constants.SUSI_NUMBER_OF_SOLVED_TASKS_FOR_POINTS:
                self.successful_semesters[user_id] = self.successful_semesters.get(user_id, 0) + 1

        self.puzzlehunt_participations_key = UserPropertyKey.objects.get(
            key_name=constants.PUZZLEHUNT_PARTICIPATIONS_KEY_NAME
        )

    def get_minimal_year_of_graduation(self, res_request, user):
        return -1

    def is_user_active(self, request, user):
        active = super(SUSIResultsGenerator, self).is_user_active(request, user)
        coefficient = self.get_user_coefficient(user, request.round)

        if self.tag.key == constants.SUSI_AGAT:
            active = active and (
                (coefficient <= constants.SUSI_AGAT_MAX_COEFFICIENT)
                and not self.get_graduation_status(user, request)
            )

        if self.tag.key == constants.SUSI_BLYSKAVICA:
            active = active and (
                (coefficient > constants.SUSI_AGAT_MAX_COEFFICIENT)
                and not (self.get_graduation_status(user, request))
            )

        if self.tag.key == constants.SUSI_CIFERSKY_CECH:
            active = active

        return active

    def deactivate_row_cells(self, request, row, cols):
        if self.tag.key == constants.SUSI_AGAT:
            # Prepare list of pairs consisting of cell and its points.
            tasks = [
                (cell, self.get_cell_total(request, cell))
                for key, cell in row.cells_by_key.items()
                if row.cells_by_key[key].active
            ]

            # Count only the best 5 tasks
            for cell, _ in sorted(tasks, key=lambda x: x[1])[:-5]:
                cell.active = False

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
        constants.SUSI_CIFERSKY_CECH: ResultsTag(
            key=constants.SUSI_CIFERSKY_CECH, name=constants.SUSI_CIFERSKY_CECH
        ),
        constants.SUSI_AGAT: ResultsTag(key=constants.SUSI_AGAT, name=constants.SUSI_AGAT),
        constants.SUSI_BLYSKAVICA: ResultsTag(
            key=constants.SUSI_BLYSKAVICA, name=constants.SUSI_BLYSKAVICA
        ),
    }

    RESULTS_GENERATOR_CLASS = SUSIResultsGenerator

    def get_actual_result_rounds(self, competition):
        active_rounds = Round.objects.filter(
            semester__competition=competition,
            visible=True,
            second_end_time__gte=timezone.now(),
        )
        if len(active_rounds) > 0:
            return active_rounds.order_by("number", "end_time")[:1]

        finished_rounds = Round.objects.filter(
            semester__competition=competition,
            visible=True,
            second_end_time__lte=timezone.now(),
            end_time__gte=timezone.now()
            - timezone.timedelta(days=MAX_DAYS_TO_SHOW_ROUND_IN_ACTUAL_RESULTS),
        )
        return finished_rounds.order_by("-end_time", "-number")[:1]

    def grade_text_submit(self, task, user, submitted_text):
        submitted_text = unidecode(submitted_text.replace(" ", "").lower())
        now = timezone.now()
        Grading = namedtuple("Grading", ["response", "points"])
        solutions = [
            unidecode(solution.replace(" ", "").lower()) for solution in task.text_submit_solution
        ]
        if submitted_text in solutions:
            response = SUBMIT_RESPONSE_OK
            points = constants.SUSI_POINTS_ALLOCATION[0]
            if (
                task.round.end_time < now <= task.round.susi_big_hint_time
                and len(task.susi_small_hint) > 0
            ):
                points -= constants.SUSI_POINTS_ALLOCATION[1]
            elif task.round.susi_big_hint_time < now and task.round.second_phase_running:
                if len(task.susi_big_hint) > 0:
                    points -= constants.SUSI_POINTS_ALLOCATION[2]
                elif len(task.susi_small_hint) > 0:
                    points -= constants.SUSI_POINTS_ALLOCATION[1]
            elif task.round.end_time < now and not task.round.second_phase_running:
                points = constants.SUSI_POINTS_ALLOCATION[3]
        else:
            response = SUBMIT_RESPONSE_WA
            points = constants.SUSI_POINTS_ALLOCATION[3]

        max_time = task.round.second_end_time
        if max_time is None:
            max_time = task.round.end_time
        wrong_submits = len(
            Submit.objects.filter(task=task, user=user, time__lte=max_time).exclude(
                text__in=solutions
            )
        )

        points = max(points - wrong_submits // constants.SUSI_WRONG_SUBMITS_TO_PENALTY, 0)

        return Grading(response, points)
