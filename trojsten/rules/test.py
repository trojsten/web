# -*- coding: utf-8 -*-

import datetime

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

import trojsten.rules.susi_constants as susi_constants
import trojsten.submit.constants as submit_constants
from trojsten.contests.models import Category, Competition, Round, Semester, Task
from trojsten.events.models import Event, EventParticipant, EventPlace, EventType
from trojsten.people.constants import SCHOOL_YEAR_END_MONTH
from trojsten.people.models import User
from trojsten.results.manager import get_results
from trojsten.results.models import Results
from trojsten.rules.kms import (
    COEFFICIENT_COLUMN_KEY,
    KMS_ALFA,
    KMS_BETA,
    KMS_CAMP_TYPE,
    KMS_MO_FINALS_TYPE,
    KMS_MO_REGIONALS_TYPE,
    KMSResultsGenerator,
    KMSRules,
)
from trojsten.rules.ksp import KSP_ALL, KSP_L1, KSP_L2, KSP_L3, KSP_L4
from trojsten.rules.models import KSPLevel
from trojsten.rules.susi import SUSIResultsGenerator, SUSIRules
from trojsten.submit.constants import SUBMIT_RESPONSE_OK
from trojsten.submit.models import Submit

SOURCE = submit_constants.SUBMIT_TYPE_SOURCE
DESCRIPTION = submit_constants.SUBMIT_TYPE_DESCRIPTION
ZIP = submit_constants.SUBMIT_TYPE_TESTABLE_ZIP


class DictObject(object):
    def __init__(self, d):
        """Convert a dictionary to a class

        @param :d Dictionary
        """
        self.__dict__.update(d)
        for k, v in d.items():
            if isinstance(v, dict):
                self.__dict__[k] = DictObject(v)
            if isinstance(v, list):
                self.__dict__[k] = [DictObject(i) for i in v if isinstance(i, dict)]


def get_scoreboard(scoreboards, tag_key):
    for scoreboard_object in scoreboards:
        scoreboard = scoreboard_object.scoreboard
        if scoreboard.tag == tag_key:
            return scoreboard
    return None


def get_row_for_user(scoreboard, user):
    if scoreboard:
        table = scoreboard.serialized_results
        for row in table["rows"]:
            if row["user"]["id"] == user.id:
                return DictObject(row)
    return None


def get_row_total(scoreboard_row, col_to_index_map):
    return float(scoreboard_row.cell_list[col_to_index_map["sum"]].points)


def get_coefficient(scoreboard_row, col_to_index_map):
    return float(scoreboard_row.cell_list[col_to_index_map[COEFFICIENT_COLUMN_KEY]].points)


def get_col_to_index_map(scoreboard):
    if scoreboard:
        return {
            k: i
            for i, k in enumerate(map(lambda c: c["key"], scoreboard.serialized_results["cols"]))
        }
    return dict()


class KMSCoefficientTest(TestCase):
    def setUp(self):
        time = datetime.datetime(2047, 4, 7, 12, 47)
        self.time = timezone.make_aware(time)

        group = Group.objects.create(name="skupina")
        self.place = EventPlace.objects.create(name="Horna dolna")
        self.type_camp = EventType.objects.create(
            name=KMS_CAMP_TYPE, organizers_group=group, is_camp=True
        )
        self.type_mo = EventType.objects.create(
            name=KMS_MO_FINALS_TYPE, organizers_group=group, is_camp=False
        )
        self.type_kkmo = EventType.objects.create(
            name=KMS_MO_REGIONALS_TYPE, organizers_group=group, is_camp=False
        )

        competition = Competition.objects.create(name="KMSTestCompetition", pk=7)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.semesters = []
        self.camps = []
        self.mo_finals = []
        self.mo_regionals = []
        for year, semester_number in [(1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2)]:
            self.semesters.append(
                Semester.objects.create(
                    year=year, number=semester_number, name="Test semester", competition=competition
                )
            )
            self.camps.append(
                Event.objects.create(
                    name="KMS camp alpha",
                    type=self.type_camp,
                    semester=self.semesters[-1],
                    place=self.place,
                    start_time=self.time,
                    end_time=self.time,
                )
            )
            if semester_number == 2:
                self.mo_finals.append(
                    Event.objects.create(
                        name="CKMO",
                        type=self.type_mo,
                        place=self.place,
                        start_time=self.time + timezone.timedelta((year - 3) * 366),
                        # CKMO ends after start of the (summer) round
                        end_time=self.time + timezone.timedelta((year - 3) * 366 + 3),
                    )
                )
            if semester_number == 1:
                self.mo_regionals.append(
                    Event.objects.create(
                        name="KKMO",
                        type=self.type_kkmo,
                        place=self.place,
                        start_time=self.time + timezone.timedelta((year - 3) * 366 - 180),
                        end_time=self.time + timezone.timedelta((year - 3) * 366 - 180),
                    )
                )
        self.current_semester = self.semesters[-1]
        self.start = self.time + timezone.timedelta(2)
        self.end = self.time + timezone.timedelta(4)
        self.round = Round.objects.create(
            number=1,
            semester=self.current_semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start,
            end_time=self.end,
        )
        self.previous_rounds = []
        for i in range(2):
            self.previous_rounds.append(
                Round.objects.create(
                    number=i,
                    semester=self.semesters[-2],
                    visible=True,
                    solutions_visible=False,
                    start_time=self.start,
                    end_time=self.end,
                )
            )

        graduation_year = self.round.end_time.year + int(
            self.round.end_time.month > SCHOOL_YEAR_END_MONTH
        )
        self.test_user = User.objects.create(
            username="test_user",
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=graduation_year + 3,
        )
        self.tag = KMSRules.RESULTS_TAGS[KMS_BETA]

        category_alfa = Category.objects.create(name=KMS_ALFA, competition=competition)
        category_beta = Category.objects.create(name=KMS_BETA, competition=competition)

        self.previous_tasks = []
        for round_ in self.previous_rounds:
            for i in range(1, 11):
                self.previous_tasks.append(
                    Task.objects.create(
                        number=i,
                        name="Test task {}".format(i),
                        round=round_,
                        description_points_visible=True,
                    )
                )
                cat = []
                if i <= 7:
                    cat += [category_alfa]
                if i >= 3:
                    cat += [category_beta]
                self.previous_tasks[-1].categories.set(cat)
                self.previous_tasks[-1].save()

    def _create_submits(self, user, points, tasks):
        for point, task in zip(points, tasks):
            if point >= 0:
                submit = Submit.objects.create(
                    task=task,
                    user=user,
                    submit_type=1,
                    points=point,
                    testing_status="reviewed",
                )
                submit.time = self.end + timezone.timedelta(-1)
                submit.save()

    def test_year_only(self):
        # Coefficient = 0: year = 3, successful semesters = 0, mo = 0, regionals=0
        self.test_user.graduation -= 2
        self.test_user.save()
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 0)

    def test_camps_only(self):
        # Coefficient = 2: year = 1, successful semesters = 2, mo = 0, regionals=0
        EventParticipant.objects.create(
            event=self.camps[3],
            user=self.test_user,
            type=EventParticipant.PARTICIPANT,
            going=True,
        )
        EventParticipant.objects.create(
            event=self.camps[4],
            user=self.test_user,
            type=EventParticipant.RESERVE,
            going=True,
        )
        # This event does not count as successful, as it happens after the semester of the current
        # round.
        EventParticipant.objects.create(
            event=self.camps[5],
            user=self.test_user,
            type=EventParticipant.PARTICIPANT,
            going=True,
        )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 2)

    def test_points_only(self):
        # Coefficient = 0, year = 1, successful semesters = 0, mo = 0, regionals = 0
        points = [0, 0, 0, 0, 0, 9, 9, 9, 9, 9]
        # # Create submits for first round's tasks
        self._create_submits(self.test_user, points, self.previous_tasks[:10])
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 0)

        # Coefficient = 1, year = 1, successful semesters = 1, mo = 0, regionals = 0
        # Create submits for second round's tasks
        self._create_submits(self.test_user, points, self.previous_tasks[10:])
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 1)

    def test_camps_mo(self):
        # Coefficient = 3: year = 4, successful semesters = 1, mo = 2, regionals=0
        self.test_user.graduation -= 3
        self.test_user.save()
        EventParticipant.objects.create(
            event=self.camps[4], user=self.test_user, type=EventParticipant.PARTICIPANT, going=True
        )
        EventParticipant.objects.create(
            event=self.camps[5], user=self.test_user, type=EventParticipant.PARTICIPANT, going=True
        )
        EventParticipant.objects.create(
            event=self.mo_finals[1],
            user=self.test_user,
            type=EventParticipant.PARTICIPANT,
            going=True,
        )
        EventParticipant.objects.create(
            event=self.mo_finals[0],
            user=self.test_user,
            type=EventParticipant.PARTICIPANT,
            going=True,
        )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 3)

    def test_invited_to_both_camps(self):
        # Coefficient = 1: year = 1, successful semesters = 1, mo = 0, regionals=0
        beta_camp = Event.objects.create(
            name="KMS camp beta",
            type=self.type_camp,
            semester=self.semesters[4],
            place=self.place,
            start_time=self.time,
            end_time=self.time,
        )
        EventParticipant.objects.create(
            event=self.camps[4], user=self.test_user, type=EventParticipant.PARTICIPANT, going=False
        )
        EventParticipant.objects.create(
            event=beta_camp, user=self.test_user, type=EventParticipant.PARTICIPANT, going=True
        )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 1)

    def test_ignore_mo_in_same_semester(self):
        # Coefficient = 2: year = 1, successful semesters = 0, mo = 2, regionals=0
        for mo_finals in self.mo_finals:
            EventParticipant.objects.create(
                event=mo_finals, user=self.test_user, type=EventParticipant.PARTICIPANT, going=True
            )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 2)

    def test_ignore_not_going_reserve(self):
        # Coefficient = 0: year = 1, successful semesters = 0, mo = 0, regionals=0
        EventParticipant.objects.create(
            event=self.camps[4], user=self.test_user, type=EventParticipant.RESERVE, going=False
        )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 0)

    def test_ignore_not_going_participant(self):
        # Coefficient = 0: year = 1, successful semesters = 0, mo = 0, regionals=0
        EventParticipant.objects.create(
            event=self.camps[4], user=self.test_user, type=EventParticipant.PARTICIPANT, going=False
        )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 0)

    def test_many_camps(self):
        # Coefficient = 5: year = 1, successful semesters = 5, mo = 0, regionals=0
        for i in range(5):
            EventParticipant.objects.create(
                event=self.camps[i],
                user=self.test_user,
                type=EventParticipant.PARTICIPANT,
                going=True,
            )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 5)

    def test_mo_regionals(self):
        # Coefficient = 1: year = 1, successful semesters = 0, mo = 0, regionals=2
        EventParticipant.objects.create(
            event=self.mo_regionals[1],
            user=self.test_user,
            type=EventParticipant.PARTICIPANT,
            going=True,
        )
        EventParticipant.objects.create(
            event=self.mo_regionals[0],
            user=self.test_user,
            type=EventParticipant.PARTICIPANT,
            going=True,
        )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 1)

    def test_mo_finals_and_regionals(self):
        # Coefficient = 3: year = 1, successful semesters = 0, mo = 2, regionals=2
        EventParticipant.objects.create(
            event=self.mo_regionals[1],
            user=self.test_user,
            type=EventParticipant.PARTICIPANT,
            going=True,
        )
        EventParticipant.objects.create(
            event=self.mo_regionals[0],
            user=self.test_user,
            type=EventParticipant.PARTICIPANT,
            going=True,
        )
        EventParticipant.objects.create(
            event=self.mo_finals[1],
            user=self.test_user,
            type=EventParticipant.PARTICIPANT,
            going=True,
        )
        EventParticipant.objects.create(
            event=self.mo_finals[0],
            user=self.test_user,
            type=EventParticipant.PARTICIPANT,
            going=True,
        )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 3)

    def test_all(self):
        # Coefficient = 8: year = 3, successful semesters = 5, mo = 2, regionals = 2
        points = [0, 0, 0, 0, 0, 9, 9, 9, 9, 9]
        # Create submits for both previous round's tasks
        self._create_submits(self.test_user, points * 2, self.previous_tasks)
        self.test_user.graduation -= 2
        self.test_user.save()
        for i in range(3):
            EventParticipant.objects.create(
                event=self.camps[i],
                user=self.test_user,
                type=EventParticipant.PARTICIPANT,
                going=True,
            )
        EventParticipant.objects.create(
            event=self.camps[3],
            user=self.test_user,
            type=EventParticipant.RESERVE,
            going=True,
        )
        for i in range(2):
            EventParticipant.objects.create(
                event=self.mo_finals[i],
                user=self.test_user,
                type=EventParticipant.PARTICIPANT,
                going=True,
            )
            EventParticipant.objects.create(
                event=self.mo_regionals[i],
                user=self.test_user,
                type=EventParticipant.PARTICIPANT,
                going=True,
            )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 8)


class KMSRulesTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="skupina")
        time = datetime.datetime(2004, 4, 7, 12, 47)
        self.time = timezone.make_aware(time)
        # pk = 7 sets rules to KMSRules
        self.competition = Competition.objects.create(name="TestCompetition", pk=7)
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.competition.save()
        self.semester = Semester.objects.create(
            number=1, name="Test semester", competition=self.competition, year=47
        )
        self.start = self.time + timezone.timedelta(-4)
        self.end = self.time + timezone.timedelta(4)
        self.round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start,
            end_time=self.end,
        )
        self.type_mo = EventType.objects.create(
            name=KMS_MO_FINALS_TYPE, is_camp=False, organizers_group=self.group
        )
        self.type_camp = EventType.objects.create(
            name=KMS_CAMP_TYPE, is_camp=True, organizers_group=self.group
        )
        self.place = EventPlace.objects.create(name="Horna dolna")

        category_alfa = Category.objects.create(name=KMS_ALFA, competition=self.competition)
        category_beta = Category.objects.create(name=KMS_BETA, competition=self.competition)

        self.tasks = []
        for i in range(1, 11):
            self.tasks.append(
                Task.objects.create(
                    number=i,
                    name="Test task {}".format(i),
                    round=self.round,
                    description_points_visible=True,
                )
            )
            cat = []
            if i <= 8:
                cat += [category_alfa]
            if i >= 3:
                cat += [category_beta]
            self.tasks[-1].categories.set(cat)
            self.tasks[-1].save()

        self.url = reverse("view_latest_results")

    def _create_submits(self, user, points):
        for i in range(len(points)):
            if points[i] >= 0:
                submit = Submit.objects.create(
                    task=self.tasks[i],
                    user=user,
                    submit_type=1,
                    points=points[i],
                    testing_status="reviewed",
                )
                submit.time = self.end + timezone.timedelta(-1)
                submit.save()

    def _create_user_with_coefficient(self, coefficient, username="test_user", use_kms_camp=False):
        graduation_year = (
            self.round.end_time.year + 3 + int(self.round.end_time.month > SCHOOL_YEAR_END_MONTH)
        )
        user = User.objects.create(
            username=username,
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=graduation_year,
        )
        if use_kms_camp and coefficient > 0:
            for i in range(coefficient):
                old_semester = Semester.objects.create(
                    number=1, name="Test semester", competition=self.competition, year=46 - i
                )
                camp = Event.objects.create(
                    name="Sustredko",
                    type=self.type_camp,
                    place=self.place,
                    start_time=self.time + timezone.timedelta(-366),
                    end_time=self.time + timezone.timedelta(-365),
                    semester=old_semester,
                )
                EventParticipant.objects.create(
                    event=camp, user=user, type=EventParticipant.PARTICIPANT, going=True
                )
        else:
            for i in range(coefficient):
                ckmo = Event.objects.create(
                    name="CKMO",
                    type=self.type_mo,
                    place=self.place,
                    start_time=self.time + timezone.timedelta(-(i + 1) * 366 - 1),
                    end_time=self.time + timezone.timedelta(-(i + 1) * 366),
                )
                EventParticipant.objects.create(
                    event=ckmo, user=user, type=EventParticipant.PARTICIPANT, going=True
                )
        return user

    def test_create_user_with_coefficient(self):
        for alfa in [False, True]:
            for i in range(0, 12 if not alfa else 9):
                user = self._create_user_with_coefficient(i, "testuser%d" % (i + 100 * alfa), alfa)
                generator = KMSResultsGenerator(KMSRules.RESULTS_TAGS[KMS_BETA])
                self.assertEqual(generator.get_user_coefficient(user, self.round), i)

    def _test_points_per_task(self, table, category):
        for coefficient, max_points in table:
            user = self._create_user_with_coefficient(
                coefficient, "testuser%d" % coefficient, use_kms_camp=category == KMS_ALFA
            )
            for task, received_points in enumerate(max_points, start=1):
                Submit.objects.all().delete()
                points = [0] * 10
                points[task - 1] = 9
                self._create_submits(user, points)
                response = self.client.get("%s?single_round=True" % self.url)
                self.assertEqual(response.status_code, 200)
                scoreboard = get_scoreboard(response.context["scoreboards"], category)
                col_to_index_map = get_col_to_index_map(scoreboard)
                row = get_row_for_user(scoreboard, user)
                self.assertEqual(
                    row.cell_list[col_to_index_map["sum"]].points,
                    str(received_points),
                    msg=f"For coefficient {coefficient}, task {task} in category {category}",
                )

    def test_alfa(self):
        table = [
            (0, [9, 9, 9, 9, 9, 9, 9, 9, 0, 0]),
            (1, [3, 6, 9, 9, 9, 9, 9, 9, 0, 0]),
            (2, [0, 3, 6, 9, 9, 9, 9, 9, 0, 0]),
        ]
        self._test_points_per_task(table, KMS_ALFA)

    def test_beta(self):
        table = [
            (1, [0, 0, 3, 6, 9, 9, 9, 9, 9, 9]),
            (2, [0, 0, 3, 6, 9, 9, 9, 9, 9, 9]),
            (3, [0, 0, 3, 6, 9, 9, 9, 9, 9, 9]),
            (4, [0, 0, 3, 6, 9, 9, 9, 9, 9, 9]),
            (6, [0, 0, 3, 6, 9, 9, 9, 9, 9, 9]),
            (7, [0, 0, 0, 3, 6, 9, 9, 9, 9, 9]),
        ]
        self._test_points_per_task(table, KMS_BETA)

    def test_only_best_five(self):
        points = [9, 7, 0, 8, 4, 5, 4]
        active = [True] * 7
        active[2] = False
        user = self._create_user_with_coefficient(0, use_kms_camp=True)
        self._create_submits(user, points)

        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_ALFA)
        col_to_index_map = get_col_to_index_map(scoreboard)
        row = get_row_for_user(scoreboard, user)
        self.assertEqual(row.cell_list[col_to_index_map[COEFFICIENT_COLUMN_KEY]].points, "0")
        self.assertEqual(row.cell_list[col_to_index_map["sum"]].points, "33")
        for i in range(1, 8):
            self.assertEqual(row.cell_list[col_to_index_map[i]].points, str(points[i - 1]))
            if i not in [5, 7]:
                self.assertEqual(row.cell_list[col_to_index_map[i]].active, active[i - 1])
        self.assertTrue(
            row.cell_list[col_to_index_map[5]].active ^ row.cell_list[col_to_index_map[7]].active
        )

    def test_beta_only_user(self):
        points = [-1, -1, 2, 3, 4, 5, 6, 7, 8]
        user = self._create_user_with_coefficient(7, use_kms_camp=True)
        self._create_submits(user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_BETA)
        col_to_index_map = get_col_to_index_map(scoreboard)
        row_beta = get_row_for_user(scoreboard, user)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_ALFA)
        row_alfa = get_row_for_user(scoreboard, user)
        self.assertTrue(row_beta.active)
        self.assertFalse(row_alfa.active)
        self.assertEqual(row_beta.cell_list[col_to_index_map[COEFFICIENT_COLUMN_KEY]].points, "7")

    def test_alfa_only_user(self):
        points = [1, 2, 3, 4, 5]
        user = self._create_user_with_coefficient(1, use_kms_camp=True)
        self._create_submits(user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_BETA)
        row_beta = get_row_for_user(scoreboard, user)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_ALFA)
        row_alfa = get_row_for_user(scoreboard, user)
        self.assertTrue(row_alfa.active)
        self.assertFalse(row_beta.active)

    def test_alfa_beta_user(self):
        points = [9, 2, 1, 4, 5, 6, 7, 8, 9, 10]
        user = self._create_user_with_coefficient(0, use_kms_camp=True)
        self._create_submits(user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_BETA)
        col_to_index_map = get_col_to_index_map(scoreboard)
        row_beta = get_row_for_user(scoreboard, user)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_ALFA)
        self.assertEqual(row_beta.cell_list[col_to_index_map["sum"]].points, "40")
        col_to_index_map = get_col_to_index_map(scoreboard)
        row_alfa = get_row_for_user(scoreboard, user)
        self.assertEqual(row_alfa.cell_list[col_to_index_map["sum"]].points, "35")


class KSPRulesOneUserTest(TestCase):
    def setUp(self):
        competition = Competition.objects.create(
            name="TestKSP", pk=2
        )  # pk = 2 sets rules to KSPRules
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.last_semester_before_level_up = Semester.objects.create(
            number=1, name="Used for setting levels", competition=competition, year=0
        )
        self.semester = Semester.objects.create(
            number=1, name="Test semester", competition=competition, year=1
        )
        self.start = timezone.now() - timezone.timedelta(days=21)
        self.end = timezone.now() - timezone.timedelta(days=14)
        self.second_end = timezone.now() - timezone.timedelta(days=7)
        self.round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start,
            end_time=self.end,
            second_end_time=self.second_end,
        )

        self.tasks = []
        for i in range(1, 9):
            task = Task.objects.create(
                number=i,
                name="Test task {}".format(i),
                round=self.round,
                description_points_visible=True,
            )
            task.save()
            self.tasks.append(task)

        self.tasks[2].integer_source_points = False
        self.tasks[2].save()

        graduation = timezone.now().year + 2
        self.user = User.objects.create(
            username="TestUser",
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=graduation,
        )

        self.url = reverse("view_latest_results")

    def _set_user_level_to(self, level):
        KSPLevel.objects.all().delete()
        KSPLevel.objects.create(
            user=self.user,
            new_level=level,
            last_semester_before_level_up=self.last_semester_before_level_up,
        )

    def test_set_and_get_user_level(self):
        level = KSPLevel.objects.for_user_in_semester(self.semester.pk, self.user.pk)
        self.assertEqual(level, 1)

        self._set_user_level_to(4)
        level = KSPLevel.objects.for_user_in_semester(self.semester.pk, self.user.pk)
        self.assertEqual(level, 4)

        self._set_user_level_to(2)
        level = KSPLevel.objects.for_user_in_semester(self.semester.pk, self.user.pk)
        self.assertEqual(level, 2)

    def _create_submits(self, submit_definitions):
        for task_number, submit_type, submit_time, points in submit_definitions:
            submit = Submit.objects.create(
                task=self.tasks[task_number - 1],
                user=self.user,
                submit_type=submit_type,
                points=points,
            )
            submit.time = submit_time
            if submit_type == DESCRIPTION:
                submit.testing_status = "reviewed"
            submit.save()

    def _assert_is_user_in_results_tables(self, in_which_tables_should_user_be):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for tag, should_be_in_table in zip(
            [KSP_ALL, KSP_L1, KSP_L2, KSP_L3, KSP_L4], in_which_tables_should_user_be
        ):
            scoreboard = get_scoreboard(response.context["scoreboards"], tag)
            row = get_row_for_user(scoreboard, self.user)
            is_in_table = row is not None and row.active
            if should_be_in_table:
                self.assertTrue(is_in_table, "User should be in results table {}".format(tag))
            else:
                self.assertFalse(is_in_table, "User should not be in results table {}".format(tag))

    def test_user_is_not_in_lower_level_results_table(self):
        self._create_submits(
            [
                (1, SOURCE, self.start + timezone.timedelta(days=1), 10),
                (2, SOURCE, self.start + timezone.timedelta(days=1), 10),
            ]
        )
        self._set_user_level_to(2)
        self._assert_is_user_in_results_tables([True, False, True, False, False])

        self._create_submits(
            [
                (7, SOURCE, self.start + timezone.timedelta(days=1), 10),
                (8, SOURCE, self.start + timezone.timedelta(days=1), 10),
            ]
        )
        self._set_user_level_to(4)
        self._assert_is_user_in_results_tables([True, False, False, False, True])

    def test_user_is_not_in_higher_level_results_table(self):
        self._create_submits(
            [
                (1, SOURCE, self.start + timezone.timedelta(days=1), 10),
                (2, SOURCE, self.start + timezone.timedelta(days=1), 10),
                (3, SOURCE, self.start + timezone.timedelta(days=1), 10),
            ]
        )
        self._set_user_level_to(1)
        self._assert_is_user_in_results_tables([True, True, False, False, False])

        self._create_submits([(4, SOURCE, self.start + timezone.timedelta(days=1), 10)])
        self._assert_is_user_in_results_tables([True, True, False, False, False])

        self._create_submits([(5, SOURCE, self.start + timezone.timedelta(days=1), 10)])
        self._assert_is_user_in_results_tables([True, True, True, False, False])

        self._set_user_level_to(3)
        self._assert_is_user_in_results_tables([True, False, False, True, False])

    def _bulk_set_task_points(self, points):
        # Use description points because task 2 has float points for source
        # and we want to have integral sum of points.
        submit_defs = [
            (i, DESCRIPTION, self.start + timezone.timedelta(days=1), points)
            for i, points in enumerate(points, start=1)
            if points is not None
        ]
        self._create_submits(submit_defs)

    def _get_point_cells_for_tasks(self, results_tag=KSP_ALL):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], results_tag)
        col_to_index_map = get_col_to_index_map(scoreboard)
        row = get_row_for_user(scoreboard, self.user)
        return {
            k: row.cell_list[col_to_index_map[k]]
            for k in map(lambda c: c["key"], scoreboard.serialized_results["cols"])
        }

    def _assert_active_cells(self, cells, which_cells_should_be_active):
        for i, should_be_active in enumerate(which_cells_should_be_active, start=1):
            if should_be_active is None:
                self.assertFalse(i in cells, "Cell for task {} should not be present.".format(i))
            elif should_be_active:
                self.assertTrue(cells[i].active, "Cell for task {} should be active".format(i))
            else:
                self.assertFalse(cells[i].active, "Cell for task {} should not be active".format(i))

    def test_count_only_best_five_tasks_user_level_1(self):
        self._bulk_set_task_points([17, 1, 8, 14, 3, 10, 15, 9])

        cells = self._get_point_cells_for_tasks(KSP_ALL)
        self.assertEqual(cells["sum"].points, str(17 + 15 + 14 + 10 + 9))
        self._assert_active_cells(cells, [True, False, False, True, False, True, True, True])

        cells = self._get_point_cells_for_tasks(KSP_L1)
        self.assertEqual(cells["sum"].points, str(17 + 15 + 14 + 10 + 9))
        self._assert_active_cells(cells, [True, False, False, True, False, True, True, True])

        cells = self._get_point_cells_for_tasks(KSP_L2)
        self.assertEqual(cells["sum"].points, str(15 + 14 + 10 + 9 + 8))
        self._assert_active_cells(cells, [None, False, True, True, False, True, True, True])

        cells = self._get_point_cells_for_tasks(KSP_L3)
        self.assertEqual(cells["sum"].points, str(15 + 14 + 10 + 9 + 8))
        self._assert_active_cells(cells, [None, None, True, True, False, True, True, True])

        cells = self._get_point_cells_for_tasks(KSP_L4)
        self.assertEqual(cells["sum"].points, str(15 + 14 + 10 + 9 + 3))
        self._assert_active_cells(cells, [None, None, None, True, True, True, True, True])

    def test_count_only_best_five_tasks_user_level_3(self):
        self._set_user_level_to(3)
        self._bulk_set_task_points([20, 18, 19, 15, 6, 3, 12, 17])

        cells = self._get_point_cells_for_tasks(KSP_ALL)
        self.assertEqual(cells["sum"].points, str(19 + 17 + 15 + 12 + 6))
        self._assert_active_cells(cells, [False, False, True, True, True, False, True, True])

        cells = self._get_point_cells_for_tasks(KSP_L3)
        self.assertEqual(cells["sum"].points, str(19 + 17 + 15 + 12 + 6))
        self._assert_active_cells(cells, [None, None, True, True, True, False, True, True])

        cells = self._get_point_cells_for_tasks(KSP_L4)
        self.assertEqual(cells["sum"].points, str(17 + 15 + 12 + 6 + 3))
        self._assert_active_cells(cells, [None, None, None, True, True, True, True, True])

    def test_submits_in_first_phase(self):
        self._create_submits(
            [
                (1, SOURCE, self.start + timezone.timedelta(days=1), 10),
                (2, SOURCE, self.start + timezone.timedelta(days=2), 8),
            ]
        )

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, "10")
        self.assertEqual(cells[2].points, "8")
        self.assertEqual(cells[3].points, "")
        self.assertEqual(cells["sum"].points, "18")

    def test_zip_submit_in_first_phase(self):
        self._create_submits([(1, ZIP, self.start + timezone.timedelta(days=1), 10)])

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, "10")
        self.assertEqual(cells["sum"].points, "10")

    def test_last_submit_in_first_phase(self):
        self._create_submits(
            [
                (1, SOURCE, self.start + timezone.timedelta(days=1), 7),
                (1, SOURCE, self.start + timezone.timedelta(days=2), 9),
                (1, SOURCE, self.start + timezone.timedelta(days=3), 6),
                (2, SOURCE, self.start + timezone.timedelta(days=1), 3),
                (2, SOURCE, self.start + timezone.timedelta(days=4), 2),
            ]
        )

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, "6")
        self.assertEqual(cells[2].points, "2")

    def test_submits_in_second_phase(self):
        self._create_submits(
            [
                (1, SOURCE, self.end + timezone.timedelta(days=1), 7),
                (2, SOURCE, self.end + timezone.timedelta(days=2), 4),
            ]
        )

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, "3.5")
        self.assertEqual(cells[2].points, "2")
        self.assertEqual(cells[3].points, "")
        self.assertEqual(cells["sum"].points, "5.5")

    def test_zip_submit_in_second_phase(self):
        self._create_submits([(1, ZIP, self.end + timezone.timedelta(days=1), 7)])

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, "3.5")
        self.assertEqual(cells["sum"].points, "3.5")

    def test_last_submit_in_second_phase(self):
        self._create_submits(
            [
                (1, SOURCE, self.end + timezone.timedelta(days=1), 8),
                (1, SOURCE, self.end + timezone.timedelta(days=2), 3),
            ]
        )
        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, "1.5")

    def test_submits_after_round_end(self):
        self._create_submits(
            [
                (1, SOURCE, self.start + timezone.timedelta(days=1), 7),
                (1, SOURCE, self.second_end + timezone.timedelta(seconds=1), 10),
                (1, SOURCE, self.second_end + timezone.timedelta(days=1), 10),
                (2, SOURCE, self.second_end + timezone.timedelta(seconds=1), 13),
                (3, SOURCE, self.end + timezone.timedelta(seconds=1), 9),
                (3, SOURCE, self.second_end + timezone.timedelta(seconds=1), 10),
            ]
        )
        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, "7")
        self.assertEqual(cells[2].points, "")
        self.assertEqual(cells[3].points, "4.50")

    def test_submits_in_all_phases(self):
        self._create_submits(
            [
                (1, SOURCE, self.start + timezone.timedelta(days=1), 6),
                (1, SOURCE, self.end + timezone.timedelta(days=1), 9),
                (1, SOURCE, self.second_end + timezone.timedelta(days=1), 10),
                (2, SOURCE, self.start + timezone.timedelta(days=1), 4),
                (2, SOURCE, self.end + timezone.timedelta(days=1), 8),
                (2, SOURCE, self.second_end + timezone.timedelta(days=1), 9),
                (3, SOURCE, self.start + timezone.timedelta(days=1), 4.32),
                (3, SOURCE, self.end + timezone.timedelta(days=1), 4.32 + 6.57),
                (3, SOURCE, self.second_end + timezone.timedelta(days=1), 20),
            ]
        )

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, "7.5")
        self.assertEqual(cells[2].points, "6")
        self.assertEqual(cells[3].points, "{:.3f}".format(4.32 + 6.57 / 2))

    def test_zip_submits_in_all_phases(self):
        self._create_submits(
            [
                (2, ZIP, self.start + timezone.timedelta(days=1), 5),
                (2, ZIP, self.end + timezone.timedelta(days=1), 8),
                (2, ZIP, self.second_end + timezone.timedelta(days=1), 10),
            ]
        )

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[2].points, "6.5")
        self.assertEqual(cells["sum"].points, "6.5")

    def test_fewer_points_in_second_phase(self):
        self._create_submits(
            [
                (1, SOURCE, self.start + timezone.timedelta(days=1), 7),
                (1, SOURCE, self.end + timezone.timedelta(days=1), 4),
                (1, SOURCE, self.second_end + timezone.timedelta(days=1), 10),
                (2, SOURCE, self.start + timezone.timedelta(days=1), 10),
                (2, SOURCE, self.end + timezone.timedelta(days=1), 0),
                (2, SOURCE, self.second_end + timezone.timedelta(days=1), 5),
            ]
        )

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].points, "7")
        self.assertEqual(cells[2].points, "10")

    def test_submits_with_desriptions(self):
        self._create_submits(
            [
                (1, SOURCE, self.start + timezone.timedelta(days=1), 6),
                (1, SOURCE, self.end + timezone.timedelta(days=1), 8),
                (1, SOURCE, self.second_end + timezone.timedelta(days=1), 10),
                (1, DESCRIPTION, self.start + timezone.timedelta(days=1), 5),
                (2, SOURCE, self.start + timezone.timedelta(days=1), 9),
                (2, SOURCE, self.end + timezone.timedelta(days=1), 10),
                (2, SOURCE, self.second_end + timezone.timedelta(days=1), 5),
                (2, DESCRIPTION, self.start + timezone.timedelta(days=1), 3),
                (2, DESCRIPTION, self.second_end + timezone.timedelta(days=1), 9),
            ]
        )

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].auto_points, "7")
        self.assertEqual(cells[1].manual_points, "5")
        self.assertEqual(cells[1].points, "12")

        self.assertEqual(cells[2].auto_points, "9.5")
        self.assertEqual(cells[2].manual_points, "9")
        self.assertEqual(cells[2].points, "18.5")

    def test_round_without_second_end(self):
        self.round.second_end_time = None
        self.round.save()

        self._create_submits(
            [
                (1, SOURCE, self.start + timezone.timedelta(days=1), 2),
                (1, SOURCE, self.start + timezone.timedelta(days=2), 6),
                (1, SOURCE, self.end + timezone.timedelta(days=1), 10),
                (1, DESCRIPTION, self.start + timezone.timedelta(days=1), 4),
                (2, SOURCE, self.start + timezone.timedelta(days=1), 9),
                (2, SOURCE, self.start + timezone.timedelta(days=2), 5),
                (2, SOURCE, self.end + timezone.timedelta(days=1), 10),
                (2, DESCRIPTION, self.start + timezone.timedelta(days=1), 3),
                (2, DESCRIPTION, self.end + timezone.timedelta(days=10), 9),
            ]
        )

        cells = self._get_point_cells_for_tasks()
        self.assertEqual(cells[1].auto_points, "6")
        self.assertEqual(cells[1].manual_points, "4")
        self.assertEqual(cells[1].points, "10")

        self.assertEqual(cells[2].auto_points, "5")
        self.assertEqual(cells[2].manual_points, "9")
        self.assertEqual(cells[2].points, "14")


class SusiCoefficientTest(TestCase):
    def setUp(self):
        time = datetime.datetime(2007, 4, 7, 12, 47)
        self.time = timezone.make_aware(time)

        group = Group.objects.create(name="skupina")
        self.place = EventPlace.objects.create(name="Horna dolna")
        self.type_camp = EventType.objects.create(
            name=susi_constants.SUSI_CAMP_TYPE, organizers_group=group, is_camp=True
        )
        self.type_camp_kms = EventType.objects.create(
            name=KMS_CAMP_TYPE, organizers_group=group, is_camp=True
        )
        self.other_camp = Event.objects.create(
            name="KMS camp",
            type=self.type_camp_kms,
            semester=None,
            place=self.place,
            start_time=self.time,
            end_time=self.time,
        )

        # pk = 9 sets rules to SUSIRules
        self.competition = Competition.objects.create(name="TestCompetition", pk=9)
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.semesters = []
        self.rounds = []
        self.tasks = []
        self.camps = []
        self.users = []
        for year, semester_number in [(1, 1), (1, 2), (3, 1), (3, 2)]:
            self.semesters.append(
                Semester.objects.create(
                    year=year,
                    number=semester_number,
                    name=f"Test semester {year}-{semester_number}",
                    competition=self.competition,
                )
            )
            self.rounds.append(
                Round.objects.create(
                    number=1,
                    semester=self.semesters[-1],
                    visible=True,
                    solutions_visible=False,
                    start_time=self.time
                    + datetime.timedelta((year - 3) * 366 + semester_number * 183 - 400),
                    end_time=self.time
                    + datetime.timedelta((year - 3) * 366 + semester_number * 183 - 300),
                )
            )
            self.tasks.append(
                [
                    Task.objects.create(
                        number=i,
                        name="Test task {}".format(i),
                        round=self.rounds[-1],
                        description_points_visible=True,
                    )
                    for i in range(1, 8)
                ]
            )
            self.camps.append(
                Event.objects.create(
                    name="Susi camp",
                    type=self.type_camp,
                    semester=self.semesters[-1],
                    place=self.place,
                    start_time=self.time + datetime.timedelta(-300),
                    end_time=self.time + datetime.timedelta(-300),
                )
            )
        self.round = self.rounds[-1]
        self.current_semester = self.semesters[-1]
        self.start = self.time + timezone.timedelta(2)
        self.end = self.time + timezone.timedelta(4)
        self.second_end = self.time + timezone.timedelta(7)

        graduation_year = self.round.end_time.year + int(
            self.round.end_time.month > SCHOOL_YEAR_END_MONTH
        )
        for i in range(4):
            self.users.append(
                User.objects.create(
                    username=f"test_user{i}",
                    password="password",
                    first_name=f"Jozko{i}",
                    last_name=f"Mrkvicka{i}",
                    graduation=graduation_year + 3,
                )
            )
        self.old_user = User.objects.create(
            username="misof",
            password="password",
            first_name="Michal",
            last_name="Forisek",
            graduation=graduation_year - 30,
        )

    def test_susi_camps_only(self):
        # Coefficient = 8: successful semesters = 0, camps = 2
        EventParticipant.objects.create(
            event=self.camps[0], user=self.users[0], type=EventParticipant.PARTICIPANT, going=True
        )
        EventParticipant.objects.create(
            event=self.camps[1], user=self.users[0], type=EventParticipant.RESERVE, going=True
        )
        for tag in susi_constants.HIGH_SCHOOL_CATEGORIES:
            generator = SUSIResultsGenerator(tag)
            self.assertEqual(
                generator.get_user_coefficient(self.users[0], self.round),
                2 * susi_constants.EXP_POINTS_FOR_SUSI_CAMP,
            )

    def test_other_camps_only(self):
        EventParticipant.objects.create(
            event=self.other_camp, user=self.users[0], type=EventParticipant.PARTICIPANT, going=True
        )
        for tag in susi_constants.HIGH_SCHOOL_CATEGORIES:
            generator = SUSIResultsGenerator(tag)
            self.assertEqual(generator.get_user_coefficient(self.users[0], self.round), 0)

    def test_ignore_not_going(self):
        EventParticipant.objects.create(
            event=self.camps[0], user=self.users[0], type=EventParticipant.PARTICIPANT, going=False
        )
        for tag in susi_constants.HIGH_SCHOOL_CATEGORIES:
            generator = SUSIResultsGenerator(tag)
            self.assertEqual(generator.get_user_coefficient(self.users[0], self.round), 0)

    def create_submit(self, semester, task, who, points):
        Submit.objects.create(
            task=self.tasks[semester - 1][task - 1],
            user=self.old_user if who == -1 else self.users[who],
            submit_type=submit_constants.SUBMIT_TYPE_TEXT,
            points=points,
            testing_status="reviewed",
        )

    def create_old_submits(self):
        """
        Semester 1:
        Misof  0 0 0 0 10
        Jozko0 0 0 0 0 9
        Jozko1 0 0 0 9 0
        Jozko2 0 0 0 0 9
        Jozko3 0 0 0 9 0

        Semester 2:
        Misof  0 0 0 0 10
        Jozko2 0 0 0 5 5
        Jozko1 0 0 0 0 8
        Jozko3 0 0 0 0 7
        Jozko0 0 0 0 0 6
        """
        self.create_submit(1, 5, -1, 10)
        self.create_submit(1, 5, 0, 9)
        self.create_submit(1, 4, 1, 9)
        self.create_submit(1, 5, 2, 9)
        self.create_submit(1, 4, 3, 9)

        self.create_submit(2, 5, -1, 10)
        self.create_submit(2, 4, 2, 5)
        self.create_submit(2, 5, 2, 5)
        self.create_submit(2, 5, 1, 8)
        self.create_submit(2, 5, 3, 7)
        self.create_submit(2, 5, 0, 6)

    def create_current_submits(self):
        # Each user including old_user (-1)
        for uid in range(-1, 4):
            self.create_submit(4, 5, uid, 9)

    def test_create_only_results_for_previous_nonfinal_rounds(self):
        self.create_old_submits()
        self.create_current_submits()
        for category in [susi_constants.SUSI_AGAT, susi_constants.SUSI_BLYSKAVICA]:
            get_results(category, self.rounds[0], single_round=False)
        self.assertEqual(
            set(table.tag for table in Results.objects.filter(round=self.rounds[0]).all()),
            {susi_constants.SUSI_AGAT, susi_constants.SUSI_BLYSKAVICA},
        )
        self.rounds[0].results_final = True
        self.rounds[0].save()
        get_results(susi_constants.SUSI_AGAT, self.round, single_round=True)
        self.assertEqual(
            set(table.tag for table in Results.objects.filter(round=self.rounds[0]).all()),
            {susi_constants.SUSI_AGAT, susi_constants.SUSI_BLYSKAVICA},
        )
        self.assertEqual(
            set(table.tag for table in Results.objects.filter(round=self.rounds[1]).all()),
            set(susi_constants.HIGH_SCHOOL_CATEGORIES),
        )

    def test_top3(self):
        self.create_old_submits()
        user_points_all = [[9, 9, 9, 9], [6, 8, 10, 7]]
        # Counts only number of top3 placements
        user_coefficients_all = [[0, 0, 0, 0], [4] * 4]
        for round_, user_points, user_coefficients, active_category in zip(
            self.rounds[:2],
            user_points_all,
            user_coefficients_all,
            # After the first round, everyone wins all categories and hence gets 4 * 3 experience points getting to category C
            [susi_constants.SUSI_AGAT, susi_constants.SUSI_CVALAJUCI],
        ):
            user_coefficients = [
                susi_constants.EXP_POINTS_FOR_GOOD_RANK * v for v in user_coefficients
            ]
            for category in susi_constants.HIGH_SCHOOL_CATEGORIES:
                scoreboard = get_results(category, round_, single_round=False)
                col_to_index_map = get_col_to_index_map(scoreboard)
                for user, points, coefficient in zip(self.users, user_points, user_coefficients):
                    row = get_row_for_user(scoreboard, user)
                    self.assertEqual(row.active, category == active_category)
                    self.assertEqual(get_row_total(row, col_to_index_map), points)
                    self.assertEqual(get_coefficient(row, col_to_index_map), coefficient)
                row = get_row_for_user(scoreboard, self.old_user)
                self.assertEqual(row.active, False)

            scoreboard = get_results(susi_constants.SUSI_OPEN, round_, single_round=False)
            col_to_index_map = get_col_to_index_map(scoreboard)
            for user, points, coefficient in zip(self.users, user_points, user_coefficients):
                row = get_row_for_user(scoreboard, user)
                self.assertEqual(row.active, True)
                self.assertEqual(get_row_total(row, col_to_index_map), points)
                self.assertEqual(get_coefficient(row, col_to_index_map), coefficient)
            row = get_row_for_user(scoreboard, self.old_user)
            self.assertEqual(row.active, True)
            self.assertEqual(get_row_total(row, col_to_index_map), 10)

        self.create_current_submits()
        # Jozko0 won hypothetically Dialnica in round 2, Jozko1-3 won Cvalajuci and Dialnica in round 2
        user_coefficients = [v * susi_constants.EXP_POINTS_FOR_GOOD_RANK for v in [4, 6, 6, 6]]
        for category in susi_constants.HIGH_SCHOOL_CATEGORIES:
            scoreboard = get_results(category, self.round, single_round=False)
            col_to_index_map = get_col_to_index_map(scoreboard)
            for user, points, coefficient in zip(self.users, user_points_all, user_coefficients):
                row = get_row_for_user(scoreboard, user)
                self.assertEqual(get_coefficient(row, col_to_index_map), coefficient)
            row = get_row_for_user(scoreboard, self.old_user)
            self.assertEqual(row.active, False)


class SUSIRulesTest(TestCase):
    def setUp(self):
        time = datetime.datetime.now()
        self.time = timezone.make_aware(time)
        # pk = 9 sets rules to SUSIRules
        self.competition = Competition.objects.create(name="TestCompetition", pk=9)
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.competition.save()
        self.semester = Semester.objects.create(
            number=1, name="Test semester", competition=self.competition, year=47
        )
        self.start = self.time + timezone.timedelta(-21)
        self.end = self.time + timezone.timedelta(4)
        self.round1 = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start,
            end_time=self.end,
            second_end_time=self.end + timezone.timedelta(7),
            susi_big_hint_time=self.end + timezone.timedelta(4),
        )
        self.round2 = Round.objects.create(
            number=2,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start,
            end_time=self.end + timezone.timedelta(7),
            second_end_time=self.end + timezone.timedelta(14),
            susi_big_hint_time=self.end + timezone.timedelta(7 + 4),
        )
        self.round_discovery = Round.objects.create(
            number=3,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start,
            end_time=self.end + timezone.timedelta(7),
            second_end_time=self.end + timezone.timedelta(14),
            susi_big_hint_time=self.end + timezone.timedelta(7 + 4),
            susi_is_discovery=True,
        )

        self.group = Group.objects.create(name="skupina")
        self.type_camp = EventType.objects.create(
            name=susi_constants.SUSI_CAMP_TYPE, organizers_group=self.group, is_camp=True
        )

        self.tasks = []
        for i in range(1, 9):
            task = Task.objects.create(
                number=i,
                name="Test task {}".format(i),
                round=self.round1,
                description_points_visible=True,
            )
            self.tasks.append(task)

        self.url = reverse("view_latest_results")

    def _create_submits(self, user, points):
        for i in range(len(points)):
            if points[i] is not None:
                submit = Submit.objects.create(
                    task=self.tasks[i],
                    user=user,
                    submit_type=submit_constants.SUBMIT_TYPE_TEXT,
                    points=points[i],
                    testing_status="reviewed",
                )
                submit.time = self.end + timezone.timedelta(-1)
                submit.save()

    def _create_user_with_coefficient(self, coefficient, username="test_user"):
        user = User.objects.create(
            username=username,
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=self.round1.end_time.year + 3,
        )
        place = EventPlace.objects.create(name="Horna dolna")
        for i in range(coefficient // susi_constants.EXP_POINTS_FOR_SUSI_CAMP):
            semester = Semester.objects.create(
                number=i + 1, name="Test semester", competition=self.competition, year=i + 1
            )
            camp = Event.objects.create(
                name="KMS camp",
                type=self.type_camp,
                semester=semester,
                place=place,
                start_time=self.time,
                end_time=self.time + timezone.timedelta(-(i + 1) * 30),
            )
            EventParticipant.objects.create(
                event=camp, user=user, type=EventParticipant.PARTICIPANT, going=True
            )
        return user

    def test_create_user_with_coefficient(self):
        for i in range(0, 24, susi_constants.EXP_POINTS_FOR_SUSI_CAMP):
            user = self._create_user_with_coefficient(i, "testuser%d" % i)
            generator = SUSIResultsGenerator(SUSIRules.RESULTS_TAGS[susi_constants.SUSI_BLYSKAVICA])
            self.assertEqual(generator.get_user_coefficient(user, self.round1), i)

    def test_high_school_user(self):
        points = [6, 2, 4, 0, 5, 1, 2, 2]
        user = self._create_user_with_coefficient(8)
        self._create_submits(user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        totals = [19, 15, 14, 10]
        for category, total in zip(susi_constants.HIGH_SCHOOL_CATEGORIES, totals):
            scoreboard = get_scoreboard(response.context["scoreboards"], category)
            row = get_row_for_user(scoreboard, user)
            col_to_index_map = get_col_to_index_map(scoreboard)
            self.assertEqual(get_row_total(row, col_to_index_map), total)
            self.assertEqual(row.active, category == susi_constants.SUSI_BLYSKAVICA)

        scoreboard = get_scoreboard(response.context["scoreboards"], susi_constants.SUSI_OPEN)
        row = get_row_for_user(scoreboard, user)
        col_to_index_map = get_col_to_index_map(scoreboard)
        self.assertEqual(get_row_total(row, col_to_index_map), sum(points))
        self.assertTrue(row.active)

    def test_cifersky_cech_user(self):
        points = [6, 2, 4, 0, 5, 1, 2, 2]
        user = self._create_user_with_coefficient(4)
        user.graduation = 10
        user.save()
        self._create_submits(user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)

        for category in susi_constants.HIGH_SCHOOL_CATEGORIES:
            scoreboard = get_scoreboard(response.context["scoreboards"], category)
            row = get_row_for_user(scoreboard, user)
            self.assertFalse(row.active)

        scoreboard = get_scoreboard(response.context["scoreboards"], susi_constants.SUSI_OPEN)
        row = get_row_for_user(scoreboard, user)
        col_to_index_map = get_col_to_index_map(scoreboard)
        self.assertEqual(get_row_total(row, col_to_index_map), sum(points))
        self.assertTrue(row.active)

    def test_results_ordering(self):
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], susi_constants.SUSI_AGAT)
        self.assertEqual(scoreboard.round.number, 1)

        self.round1.end_time = self.time + timezone.timedelta(-14)
        self.round1.second_end_time = self.time + timezone.timedelta(-7)
        self.round1.save()
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], susi_constants.SUSI_AGAT)
        self.assertEqual(scoreboard.round.number, 2)

        self.round2.end_time = self.time + timezone.timedelta(-7)
        self.round2.second_end_time = self.time + timezone.timedelta(-1)
        self.round2.save()
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], susi_constants.SUSI_AGAT)
        self.assertEqual(scoreboard.round.number, 3)

        self.round_discovery.end_time = self.time + timezone.timedelta(-7)
        self.round_discovery.second_end_time = self.time + timezone.timedelta(-1)
        self.round_discovery.save()
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], susi_constants.SUSI_AGAT)
        self.assertEqual(scoreboard.round.number, 3)

    def test_grading_with_hints(self):
        user = self._create_user_with_coefficient(1)
        task = self.tasks[0]
        task.description_points = 9
        task.text_submit_solution = ["solution"]

        points = susi_constants.POINTS_ALLOCATION
        points = [points[0], points[0] - points[1], points[0] - points[2], points[3]]
        for small_hint, big_hint, points_idx in [
            ["", "", [0, 0, 0, 3]],
            ["SMALL_HINT", "", [0, 1, 1, 3]],
            ["", "BIG_HINT", [0, 0, 2, 3]],
            ["SMALL_HINT", "BIG_HINT", [0, 1, 2, 3]],
        ]:
            task.susi_small_hint = small_hint
            task.susi_big_hint = big_hint
            task.save()

            task.round.end_time = timezone.now() + timezone.timedelta(days=1)
            task.round.susi_big_hint_time = timezone.now() + timezone.timedelta(days=2)
            task.round.second_end_time = timezone.now() + timezone.timedelta(days=3)
            grading = self.competition.rules.grade_text_submit(task, user, "solution")
            self.assertEqual(grading.response, SUBMIT_RESPONSE_OK)
            self.assertEqual(grading.points, points[points_idx[0]])

            task.round.end_time = timezone.now() + timezone.timedelta(days=-3)
            task.round.susi_big_hint_time = timezone.now() + timezone.timedelta(days=2)
            task.round.second_end_time = timezone.now() + timezone.timedelta(days=3)
            task.round.save()
            grading = self.competition.rules.grade_text_submit(task, user, "solution")
            self.assertEqual(grading.response, SUBMIT_RESPONSE_OK)
            self.assertEqual(grading.points, points[points_idx[1]])

            task.round.end_time = timezone.now() + timezone.timedelta(days=-3)
            task.round.susi_big_hint_time = timezone.now() + timezone.timedelta(days=-2)
            task.round.second_end_time = timezone.now() + timezone.timedelta(days=3)
            task.round.save()
            grading = self.competition.rules.grade_text_submit(task, user, "solution")
            self.assertEqual(grading.response, SUBMIT_RESPONSE_OK)
            self.assertEqual(grading.points, points[points_idx[2]])

            task.round.end_time = timezone.now() + timezone.timedelta(days=-3)
            task.round.susi_big_hint_time = timezone.now() + timezone.timedelta(days=-2)
            task.round.second_end_time = timezone.now() + timezone.timedelta(days=-1)
            task.round.save()
            grading = self.competition.rules.grade_text_submit(task, user, "solution")
            self.assertEqual(grading.response, SUBMIT_RESPONSE_OK)
            self.assertEqual(grading.points, points[points_idx[3]])


class TextSubmitTest(TestCase):
    def setUp(self):
        time = datetime.datetime.now()
        self.time = timezone.make_aware(time)
        self.competition = Competition.objects.create(name="TestCompetition")
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.competition.save()
        self.semester = Semester.objects.create(
            number=1, name="Test semester", competition=self.competition, year=47
        )
        self.start = self.time + timezone.timedelta(-4)
        self.end = self.time + timezone.timedelta(4)
        self.round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start,
            end_time=self.end,
        )

        graduation_year = self.round.end_time.year + int(
            self.round.end_time.month > SCHOOL_YEAR_END_MONTH
        )
        self.test_user = User.objects.create(
            username="test_user",
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=graduation_year + 3,
        )
        self.solutions = ["s", "so", "sol", "solutions"]

    def test_grade_text_submit(self):
        points = 6
        task = Task.objects.create(
            number=1,
            name="Test task",
            round=self.round,
            description_points=points,
            description_points_visible=True,
            text_submit_solution=["a"],
        )
        for real_solution in self.solutions:
            task.text_submit_solution = [real_solution]
            task.save()
            for user_solution in self.solutions:
                grading = self.competition.rules.grade_text_submit(
                    task, self.test_user, user_solution
                )
                if real_solution == user_solution:
                    self.assertEqual(grading.response, submit_constants.SUBMIT_RESPONSE_OK)
                    self.assertEqual(grading.points, points)
                else:
                    self.assertEqual(grading.response, submit_constants.SUBMIT_RESPONSE_WA)
                    self.assertEqual(grading.points, 0)

    def test_grade_text_in_susi_ignores_diacritic(self):
        points = susi_constants.POINTS_ALLOCATION[0]
        solutions = {
            "mačka": 1,
            "Macka": 1,
            "mac ka": 1,
            "ma čka": 1,
            "macká": 1,
            "mackab": 2,
            "mack": 3,
            "mačk": 3,
            "maška": 4,
        }
        task = Task.objects.create(
            number=1,
            name="Test task",
            round=self.round,
            description_points=points,
            description_points_visible=True,
            text_submit_solution=["a"],
        )
        rules = SUSIRules()
        self.round.susi_big_hint_time = self.round.end_time + datetime.timedelta(days=4)
        self.round.second_end_time = self.round.end_time + datetime.timedelta(days=7)
        self.round.save()
        for real_solution, real_eq_class in solutions.items():
            task.text_submit_solution = [real_solution]
            task.save()
            for user_solution, user_eq_class in solutions.items():
                grading = rules.grade_text_submit(task, self.test_user, user_solution)
                if real_eq_class == user_eq_class:
                    self.assertEqual(grading.response, submit_constants.SUBMIT_RESPONSE_OK)
                    self.assertEqual(grading.points, points)
                else:
                    self.assertEqual(grading.response, submit_constants.SUBMIT_RESPONSE_WA)
                    self.assertEqual(grading.points, 0)
