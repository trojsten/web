# -*- coding: utf-8 -*-

from collections import namedtuple
from logging import getLogger

from django.db.models import Count, Q
from django.utils import timezone
from unidecode import unidecode

import trojsten.rules.susi_constants as constants
from trojsten.contests.models import Round, Semester
from trojsten.events.models import EventParticipant
from trojsten.results.constants import (
    COEFFICIENT_COLUMN_KEY,
    MAX_DAYS_TO_SHOW_ROUND_IN_ACTUAL_RESULTS,
)
from trojsten.results.generator import CategoryTagKeyGeneratorMixin, ResultsGenerator
from trojsten.results.helpers import get_total_score_column_index
from trojsten.results.manager import get_results
from trojsten.results.models import Results
from trojsten.results.representation import ResultsCell, ResultsCol, ResultsTag
from trojsten.submit.constants import SUBMIT_RESPONSE_OK, SUBMIT_RESPONSE_WA
from trojsten.submit.models import Submit

from .default import CompetitionRules


def get_results_if_exist(category, round):
    if round.results_final:
        try:
            return Results.objects.get(round=round, tag=category, is_single_round=False)
        except Results.DoesNotExist:
            return None
    return get_results(category, round, single_round=False)


class SUSIResultsGenerator(CategoryTagKeyGeneratorMixin, ResultsGenerator):
    def __init__(self, tag):
        super(SUSIResultsGenerator, self).__init__(tag)
        self.susi_camps = None
        self.successful_semesters = None
        self.which_semesters = None
        self.coefficients = {}

    def get_results_level(self):
        if self.tag.key not in constants.HIGH_SCHOOL_CATEGORIES:
            return 0
        return constants.HIGH_SCHOOL_CATEGORIES.index(self.tag.key) + 1

    def get_user_coefficient(self, user, round):
        if user not in self.coefficients:
            if not self.susi_camps:
                self.prepare_coefficients(round)

            no_of_susi_camps = self.susi_camps.get(user.pk, 0)
            no_of_successful_semesters = self.successful_semesters.get(user.pk, 0)
            self.coefficients[user] = (
                constants.EXP_POINTS_FOR_SUSI_CAMP * no_of_susi_camps
                + constants.EXP_POINTS_FOR_GOOD_RANK * no_of_successful_semesters
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

        # We ignore camps that happened before YEARS_OF_CAMPS_HISTORY years, so we don't
        # produce too big dictionaries of users.
        self.susi_camps = dict(
            EventParticipant.objects.filter(
                event__type__name=constants.SUSI_CAMP_TYPE,
                event__end_time__lt=round.semester.start_time,
                event__end_time__year__gte=round.end_time.year - constants.YEARS_OF_CAMPS_HISTORY,
                going=True,
            )
            .exclude(type=EventParticipant.ORGANIZER)
            .values("user")
            .annotate(camps=Count("event__semester", distinct=True))
            .values_list("user", "camps")
        )

        semesters = Semester.objects.filter(
            Q(competition=round.semester.competition),
            Q(year__gte=round.semester.year - constants.YEARS_OF_CAMPS_HISTORY),
            Q(year__lt=round.semester.year)
            | Q(
                year=round.semester.year,
                number__lt=round.semester.number,
            ),
        ).all()
        self.successful_semesters = {}
        self.which_semesters = {}

        for semester in semesters:
            round = Round.objects.filter(semester=semester).order_by("number").last()
            if round is None:
                continue  # semester with no rounds
            result_tables = [
                (get_results_if_exist(category, round), category)
                for category in constants.HIGH_SCHOOL_CATEGORIES
            ]
            result_tables = [table for table in result_tables if table[0] is not None]

            seen_users = set()
            for table, category in result_tables:
                total_score_column_index = get_total_score_column_index(table)
                if total_score_column_index is None:
                    getLogger("management_commands").warning(
                        'Results table {} for round {} does not contain "sum" column.'.format(
                            table.tag, table.round
                        )
                    )
                    continue

                # Keep track of users which have already been seen as active
                # for them we are currently processing result tables of
                # higher or equal category than they are in
                winner_count = 0
                last_points = -1
                for row in table.serialized_results["rows"]:
                    user_id = row["user"]["id"]
                    if row["active"]:
                        seen_users.add(user_id)
                    if user_id in seen_users:
                        winner_count += 1
                        cur_points = float(row["cell_list"][total_score_column_index]["points"])
                        if winner_count <= constants.TOP_RANK_FOR_EXP or last_points == cur_points:
                            self.successful_semesters[user_id] = (
                                self.successful_semesters.get(user_id, 0) + 1
                            )
                            self.which_semesters.setdefault(user_id, []).append(
                                (semester, category)
                            )
                        last_points = cur_points

    def get_minimal_year_of_graduation(self, res_request, user):
        return -1

    def is_user_active(self, request, user):
        active = super(SUSIResultsGenerator, self).is_user_active(request, user)
        if self.tag.key == constants.SUSI_OPEN:
            return active
        if not active or self.get_graduation_status(user, request):
            return False

        coefficient = self.get_user_coefficient(user, request.round)
        user_category = next(
            category
            for category, limit in zip(
                constants.HIGH_SCHOOL_CATEGORIES, constants.COEFFICIENT_LIMITS
            )
            if coefficient < limit
        )
        return self.tag.key == user_category

    def deactivate_row_cells(self, request, row, cols):
        if self.tag.key == constants.SUSI_OPEN:
            return

        # Prepare list of pairs consisting of cell and its points.
        tasks = [
            (cell, self.get_cell_total(request, cell))
            for key, cell in row.cells_by_key.items()
            if row.cells_by_key[key].active
        ]

        # Don't count tasks below your level
        # for task_number in row.cells_by_key:
        #    if task_number < self.get_results_level():
        #        row.cells_by_key[task_number].active = False

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
        constants.SUSI_OPEN: ResultsTag(key=constants.SUSI_OPEN, name=constants.SUSI_OPEN),
        constants.SUSI_OLD_CIFERSKY_CECH: ResultsTag(
            key=constants.SUSI_OLD_CIFERSKY_CECH, name=constants.SUSI_OLD_CIFERSKY_CECH
        ),
        constants.SUSI_AGAT: ResultsTag(key=constants.SUSI_AGAT, name=constants.SUSI_AGAT),
        constants.SUSI_BLYSKAVICA: ResultsTag(
            key=constants.SUSI_BLYSKAVICA, name=constants.SUSI_BLYSKAVICA
        ),
        constants.SUSI_CVALAJUCI: ResultsTag(
            key=constants.SUSI_CVALAJUCI, name=constants.SUSI_CVALAJUCI
        ),
        constants.SUSI_DIALNICA: ResultsTag(
            key=constants.SUSI_DIALNICA, name=constants.SUSI_DIALNICA
        ),
    }

    RESULTS_GENERATOR_CLASS = SUSIResultsGenerator

    def get_results_tags(self, year=None):
        if year is not None and year < constants.YEAR_SINCE_FOUR_CATEGORIES:
            tags = [
                constants.SUSI_OLD_CIFERSKY_CECH,
                constants.SUSI_AGAT,
                constants.SUSI_BLYSKAVICA,
            ]
        else:
            tags = [
                constants.SUSI_OPEN,
                constants.SUSI_AGAT,
                constants.SUSI_BLYSKAVICA,
                constants.SUSI_CVALAJUCI,
                constants.SUSI_DIALNICA,
            ]
        return (self.RESULTS_TAGS[tag_key] for tag_key in tags)

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
            points = constants.POINTS_ALLOCATION[0]
            big_hint_time = task.round.susi_big_hint_time or task.round.end_time
            if task.round.end_time < now <= big_hint_time and len(task.susi_small_hint) > 0:
                points -= constants.POINTS_ALLOCATION[1]
            elif big_hint_time < now and task.round.second_phase_running:
                if len(task.susi_big_hint) > 0:
                    points -= constants.POINTS_ALLOCATION[2]
                elif len(task.susi_small_hint) > 0:
                    points -= constants.POINTS_ALLOCATION[1]
            elif task.round.end_time < now and not task.round.second_phase_running:
                points = constants.POINTS_ALLOCATION[3]
        else:
            response = SUBMIT_RESPONSE_WA
            points = constants.POINTS_ALLOCATION[3]

        max_time = task.round.second_end_time
        if max_time is None:
            max_time = task.round.end_time
        wrong_submits = len(
            Submit.objects.filter(task=task, user=user, time__lte=max_time).exclude(
                text__in=solutions
            )
        )

        points = max(points - wrong_submits // constants.WRONG_SUBMITS_TO_PENALTY, 0)

        return Grading(response, points)
