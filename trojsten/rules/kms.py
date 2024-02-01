# -*- coding: utf-8 -*-

from collections import namedtuple
from decimal import Decimal
from logging import getLogger

from django.db.models import Count, Q

from trojsten.contests.models import Semester
from trojsten.events.models import EventParticipant
from trojsten.results.constants import COEFFICIENT_COLUMN_KEY
from trojsten.results.generator import CategoryTagKeyGeneratorMixin, ResultsGenerator
from trojsten.results.helpers import get_total_score_column_index
from trojsten.results.manager import get_results, get_results_tags_for_rounds
from trojsten.results.representation import ResultsCell, ResultsCol, ResultsTag
from trojsten.submit.models import Submit

from .default import CompetitionRules
from .default import FinishedRoundsResultsRulesMixin as FinishedRounds

KMS_ALFA = "alfa"
KMS_BETA = "beta"

KMS_POINTS_FOR_SUCCESSFUL_SEMESTER = 90

KMS_ALFA_MAX_COEFFICIENT = 2
KMS_FULL_POINTS_COEFFICIENT_BOUND = [0, 0, 0, 1, 2, 6, 100, 100, 100, 100, 100]
KMS_BETA_MULTIPLIER_BOUND = [0, 0, 0, 1, 2, 3, 3, 3, 3, 3, 3]
KMS_ELIGIBLE_FOR_TASK_BOUND = [0, 1, 2, 6, 100, 100, 100, 100, 100, 100, 100]
KMS_CAMP_TYPE = "KMS sústredenie"
KMS_MO_FINALS_TYPE = "CKMO"
KMS_MO_REGIONALS_TYPE = "KKMO"

KMS_YEARS_OF_CAMPS_HISTORY = 10


class KMSResultsGenerator(CategoryTagKeyGeneratorMixin, ResultsGenerator):
    def __init__(self, tag):
        super(KMSResultsGenerator, self).__init__(tag)
        self.successful_semesters = None
        self.mo_finals = None
        self.mo_regionals = None
        self.coefficients = {}

    def get_user_coefficient(self, user, round):
        if user not in self.coefficients:
            if not self.successful_semesters or not self.mo_finals or not self.mo_regionals:
                self.prepare_coefficients(round)

            successful_semesters = self.successful_semesters.get(user.pk, 0)
            mo_finals = self.mo_finals.get(user.pk, 0)
            mo_regionals = self.mo_regionals.get(user.pk, 0)
            self.coefficients[user] = min(1, mo_regionals) + successful_semesters + mo_finals

        return self.coefficients[user]

    def prepare_coefficients(self, round):
        """
        Fetch from the db number of successful semester and number of participation
        in MO finals and regionals for each user and store them in dictionaries. The prepared
        data in dictionaries are used to compute the coefficient of a given user.
        We consider only events happened before given round, so the coefficients are computed
        correct in older results.
        """
        # We count only MO finals in previous school years, the user coefficient remains the same
        # during a semester. We assume that the MO finals are held in the last semester
        # of a year.
        semester_start = round.semester.start_time

        self.mo_finals = dict(
            EventParticipant.objects.filter(
                event__type__name=KMS_MO_FINALS_TYPE, event__end_time__lt=semester_start
            )
            .values("user")
            .annotate(mo_finals=Count("event"))
            .values_list("user", "mo_finals")
        )
        self.mo_regionals = dict(
            EventParticipant.objects.filter(
                event__type__name=KMS_MO_REGIONALS_TYPE, event__end_time__lt=semester_start
            )
            .values("user")
            .annotate(mo_regionals=Count("event"))
            .values_list("user", "mo_regionals")
        )
        self.successful_semesters = dict()

        # Get a QuerySet of old semesters. We ignore semesters that happened before
        # KMS_YEARS_OF_CAMPS_HISTORY years, so we don't produce too big dictionaries of users.
        old_semesters = Semester.objects.filter(
            Q(
                competition=round.semester.competition,
                year__gte=round.semester.year - KMS_YEARS_OF_CAMPS_HISTORY,
            ),
            Q(year__lt=round.semester.year)
            | Q(
                year=round.semester.year,
                number__lt=round.semester.number,
            ),
        )

        # Get last round results (for each category) and events for each old semester
        ResultsAndEventsObject = namedtuple("ResultsAndEventsObject", ["results", "events"])
        results_and_event_objects = list()
        for semester in old_semesters:
            last_round = semester.round_set.order_by("number").last()
            if last_round is None:
                last_round_results = []
            else:
                last_round_results = [
                    get_results(result_tag.key, last_round, False)
                    for result_tag in list(get_results_tags_for_rounds([last_round]))[0]
                ]
            events = semester.event_set.filter(type__name=KMS_CAMP_TYPE)
            results_and_event_objects.append(
                ResultsAndEventsObject(results=last_round_results, events=events)
            )

        # Process events and results of each category by semester
        for results_and_event_object in results_and_event_objects:
            successful = set()
            for event in results_and_event_object.events:
                successful = successful.union(
                    list(event.participants.values_list("user_id", flat=True))
                )
            for scoreboard in results_and_event_object.results:
                # Get the column with total score for the scoreboard
                total_score_column_index = get_total_score_column_index(scoreboard)
                if total_score_column_index is None:
                    getLogger("management_commands").warning(
                        'Results table {} for round {} does not contain "sum" column.'.format(
                            scoreboard.tag, scoreboard.round
                        )
                    )
                    continue

                # Check points of each user, mark his semester as successful if they are above
                # KMS_POINTS_FOR_SUCCESSFUL_SEMESTER.
                for row in scoreboard.serialized_results.get("rows"):
                    user_id = row.get("user").get("id")
                    if user_id not in successful:
                        points = float(row.get("cell_list")[total_score_column_index].get("points"))
                        if points >= KMS_POINTS_FOR_SUCCESSFUL_SEMESTER:
                            successful.add(user_id)

            for user_id in successful:
                self.successful_semesters[user_id] = self.successful_semesters.get(user_id, 0) + 1

    def get_multiplier(self, key, coefficient):
        multiplier = 0
        if coefficient <= KMS_FULL_POINTS_COEFFICIENT_BOUND[key]:
            multiplier = 3
        elif key <= 9 and coefficient <= KMS_FULL_POINTS_COEFFICIENT_BOUND[key + 1]:
            multiplier = 2
        elif key <= 8 and coefficient <= KMS_FULL_POINTS_COEFFICIENT_BOUND[key + 2]:
            multiplier = 1
        if self.tag.key == KMS_BETA:
            multiplier = min(multiplier, KMS_BETA_MULTIPLIER_BOUND[key])
        return multiplier

    def get_cell_points_for_row_total(self, res_request, cell, key, coefficient):
        points = self.get_cell_total(res_request, cell)
        multiplier = self.get_multiplier(key, coefficient)
        return round(Decimal(multiplier) * points / 3, 0)

    def run(self, res_request):
        self.prepare_coefficients(res_request.round)
        res_request.has_submit_in_beta = set()
        for submit in Submit.objects.filter(
            task__round__semester=res_request.round.semester, task__number__in=[9, 10]
        ).select_related("user"):
            res_request.has_submit_in_beta.add(submit.user)
        return super(KMSResultsGenerator, self).run(res_request)

    def is_user_active(self, request, user):
        active = super(KMSResultsGenerator, self).is_user_active(request, user)
        coefficient = self.get_user_coefficient(user, request.round)

        if self.tag.key == KMS_ALFA:
            active = (
                active
                and coefficient <= KMS_ALFA_MAX_COEFFICIENT
                and self.mo_finals.get(user.pk, 0) == 0
            )

        if self.tag.key == KMS_BETA:
            active = active and (
                coefficient > KMS_ALFA_MAX_COEFFICIENT
                or user in request.has_submit_in_beta
                or self.mo_finals.get(user.pk, 0) > 0
            )

        return active

    def deactivate_row_cells(self, request, row, cols):
        coefficient = self.get_user_coefficient(row.user, request.round)

        # Count only tasks your coefficient is eligible for
        for key, cell in row.cells_by_key.items():
            counted_points = self.get_cell_points_for_row_total(request, cell, key, coefficient)
            if counted_points == 0:
                cell.active = False

        # Prepare list of pairs consisting of cell and its points.
        tasks = [
            (cell, self.get_cell_points_for_row_total(request, cell, key, coefficient))
            for key, cell in row.cells_by_key.items()
            if cell.active
        ]

        # Count only the best 5 tasks
        for cell, _ in sorted(tasks, key=lambda x: x[1])[:-5]:
            cell.active = False

    def calculate_row_round_total(self, res_request, row, cols):
        coefficient = self.get_user_coefficient(row.user, res_request.round)

        row.round_total = sum(
            self.get_cell_points_for_row_total(res_request, cell, key, coefficient)
            for key, cell in row.cells_by_key.items()
            if cell.active
        )

    def add_special_row_cells(self, res_request, row, cols):
        super(KMSResultsGenerator, self).add_special_row_cells(res_request, row, cols)
        coefficient = self.get_user_coefficient(row.user, res_request.round)
        row.cells_by_key[COEFFICIENT_COLUMN_KEY] = ResultsCell(str(coefficient))

    def create_results_cols(self, res_request):
        yield ResultsCol(key=COEFFICIENT_COLUMN_KEY, name="K.")
        for col in super(KMSResultsGenerator, self).create_results_cols(res_request):
            yield col


class KMSRules(FinishedRounds, CompetitionRules):
    RESULTS_TAGS = {
        KMS_ALFA: ResultsTag(key=KMS_ALFA, name="Alfa"),
        KMS_BETA: ResultsTag(key=KMS_BETA, name="Beta"),
    }

    RESULTS_GENERATOR_CLASS = KMSResultsGenerator
