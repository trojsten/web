# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

import trojsten.submit.constants as submit_constants
from trojsten.contests.models import Category, Competition, Round, Semester, Task
from trojsten.events.models import Event, EventParticipant, EventPlace, EventType
from trojsten.people.constants import SCHOOL_YEAR_END_MONTH
from trojsten.people.models import User
from trojsten.rules.kms import (
    COEFFICIENT_COLUMN_KEY,
    KMS_ALFA,
    KMS_BETA,
    KMS_CAMP_TYPE,
    KMS_MO_FINALS_TYPE,
    KMSResultsGenerator,
    KMSRules,
)
from trojsten.rules.ksp import KSP_ALL, KSP_L1, KSP_L2, KSP_L3, KSP_L4
from trojsten.rules.models import KSPLevel
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

        competition = Competition.objects.create(name="TestCompetition")
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.semesters = []
        self.camps = []
        self.mo_finals = []
        for (year, semester_number) in [(1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2)]:
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
                        end_time=self.time + timezone.timedelta((year - 3) * 366),
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

    def test_year_only(self):
        # Coefficient = 3: year = 3, successful semesters = 0, mo = 0
        self.test_user.graduation -= 2
        self.test_user.save()
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 3)

    def test_camps_only(self):
        # Coefficient = 3: year = 1, successful semesters = 2, mo = 0
        EventParticipant.objects.create(
            event=self.camps[5], user=self.test_user, type=EventParticipant.PARTICIPANT, going=True
        )
        EventParticipant.objects.create(
            event=self.camps[4], user=self.test_user, type=EventParticipant.PARTICIPANT, going=True
        )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 3)

    def test_camps_mo(self):
        # Coefficient = 7: year = 4, successful semesters = 1, mo = 2
        self.test_user.graduation -= 3
        self.test_user.save()
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
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 7)

    def test_invited_to_both_camps(self):
        # Coefficient = 2: year = 1, successful semesters = 1, mo = 0
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
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 2)

    def test_ignore_mo_in_same_semester(self):
        # Coefficient = 3: year = 1, successful semesters = 0, mo = 2
        for mo_finals in self.mo_finals:
            EventParticipant.objects.create(
                event=mo_finals, user=self.test_user, type=EventParticipant.PARTICIPANT, going=True
            )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 3)

    def test_ignore_not_going_reserve(self):
        # Coefficient = 1: year = 1, successful semesters = 0, mo = 0
        EventParticipant.objects.create(
            event=self.camps[4], user=self.test_user, type=EventParticipant.RESERVE, going=False
        )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 1)

    def test_count_not_going_participant(self):
        # Coefficient = 2: year = 1, successful semesters = 1, mo = 0
        EventParticipant.objects.create(
            event=self.camps[4], user=self.test_user, type=EventParticipant.PARTICIPANT, going=False
        )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 2)

    def test_many_camps(self):
        # Coefficient = 6: year = 1, successful semesters = 5, mo = 0
        for i in range(5):
            EventParticipant.objects.create(
                event=self.camps[i],
                user=self.test_user,
                type=EventParticipant.PARTICIPANT,
                going=True,
            )
        generator = KMSResultsGenerator(self.tag)
        self.assertEqual(generator.get_user_coefficient(self.test_user, self.round), 6)


class KMSRulesTest(TestCase):
    def setUp(self):
        time = datetime.datetime(2004, 4, 7, 12, 47)
        self.time = timezone.make_aware(time)
        # pk = 2 sets rules to KMSRules
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

        category_alfa = Category.objects.create(name=KMS_ALFA, competition=self.competition)
        category_beta = Category.objects.create(name=KMS_BETA, competition=self.competition)

        self.tasks = []
        for i in range(1, 11):
            self.tasks.append(
                Task.objects.create(number=i, name="Test task {}".format(i), round=self.round)
            )
            cat = []
            if i <= 7:
                cat += [category_alfa]
            if i >= 3:
                cat += [category_beta]
            self.tasks[-1].categories.set(cat)
            self.tasks[-1].save()

        self.group = Group.objects.create(name="skupina")
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

    def _create_user_with_coefficient(self, coefficient, username="test_user"):
        graduation_year = (
            self.round.end_time.year + 3 + int(self.round.end_time.month > SCHOOL_YEAR_END_MONTH)
        )
        if coefficient < 4:
            graduation_year -= coefficient - 1
        else:
            graduation_year -= 3
            type_mo = EventType.objects.create(
                name=KMS_MO_FINALS_TYPE, is_camp=False, organizers_group=self.group
            )
            place = EventPlace.objects.create(name="Horna dolna")
        user = User.objects.create(
            username=username,
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=graduation_year,
        )
        for i in range(coefficient - 4):
            ckmo = Event.objects.create(
                name="CKMO",
                type=type_mo,
                place=place,
                start_time=self.time,
                end_time=self.time + timezone.timedelta(-(i + 1) * 366),
            )
            EventParticipant.objects.create(
                event=ckmo, user=user, type=EventParticipant.PARTICIPANT, going=True
            )
        return user

    def test_create_user_with_coefficient(self):
        for i in range(-4, 12):
            user = self._create_user_with_coefficient(i, "testuser%d" % i)
            generator = KMSResultsGenerator(KMSRules.RESULTS_TAGS[KMS_BETA])
            self.assertEqual(generator.get_user_coefficient(user, self.round), i)

    def test_only_best_five(self):
        points = [9, 7, 0, 8, 4, 5, 4]
        active = [True] * 7
        active[2] = False
        user = self._create_user_with_coefficient(1)
        self._create_submits(user, points)

        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_ALFA)
        col_to_index_map = get_col_to_index_map(scoreboard)
        row = get_row_for_user(scoreboard, user)
        self.assertEqual(row.cell_list[col_to_index_map[COEFFICIENT_COLUMN_KEY]].points, "1")
        self.assertEqual(row.cell_list[col_to_index_map["sum"]].points, "33")
        for i in range(1, 8):
            self.assertEqual(row.cell_list[col_to_index_map[i]].points, str(points[i - 1]))
            if i not in [5, 7]:
                self.assertEqual(row.cell_list[col_to_index_map[i]].active, active[i - 1])
        self.assertTrue(
            row.cell_list[col_to_index_map[5]].active ^ row.cell_list[col_to_index_map[7]].active
        )

    def test_only_best_five_halved_points(self):
        points = [-1, -1, -1, 9, 6, 8, 9, 9, 2, 10]
        active = [True] * 11
        active[5] = False
        active[9] = False
        user = self._create_user_with_coefficient(9)
        self._create_submits(user, points)

        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_BETA)
        col_to_index_map = get_col_to_index_map(scoreboard)
        row = get_row_for_user(scoreboard, user)
        self.assertEqual(row.cell_list[col_to_index_map[COEFFICIENT_COLUMN_KEY]].points, "9")
        self.assertEqual(row.cell_list[col_to_index_map["sum"]].points, "41")
        for i in range(4, 11):
            self.assertEqual(row.cell_list[col_to_index_map[i]].points, str(points[i - 1]))
            self.assertEqual(row.cell_list[col_to_index_map[i]].active, active[i])
        self.assertTrue(
            row.cell_list[col_to_index_map[5]].active ^ row.cell_list[col_to_index_map[7]].active
        )

    def test_alfa_coeff_2(self):
        points = [9, 2, 3, 4, 5]
        user = self._create_user_with_coefficient(2)
        self._create_submits(user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_ALFA)
        col_to_index_map = get_col_to_index_map(scoreboard)
        row = get_row_for_user(scoreboard, user)
        for i in range(1, 6):
            self.assertTrue(row.cell_list[col_to_index_map[i]].active)
        self.assertEqual(row.cell_list[col_to_index_map["sum"]].points, "19")

    def test_alfa_coeff_3(self):
        points = [1, 2, 3, 4, 5, 6]
        user = self._create_user_with_coefficient(3)
        self._create_submits(user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_ALFA)
        col_to_index_map = get_col_to_index_map(scoreboard)
        row = get_row_for_user(scoreboard, user)
        for i in range(1, 2):
            self.assertFalse(row.cell_list[col_to_index_map[i]].active)
        for i in range(2, 7):
            self.assertTrue(row.cell_list[col_to_index_map[i]].active)
        self.assertEqual(row.cell_list[col_to_index_map["sum"]].points, "19")

    def test_beta_coeff_4(self):
        points = [-1, -1, 8, 4, 5, 6, 7]
        user = self._create_user_with_coefficient(4)
        self._create_submits(user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_BETA)
        col_to_index_map = get_col_to_index_map(scoreboard)
        row = get_row_for_user(scoreboard, user)
        for i in range(3, 8):
            self.assertTrue(row.cell_list[col_to_index_map[i]].active)
        self.assertEqual(row.cell_list[col_to_index_map["sum"]].points, "26")

    def test_beta_coeff_8(self):
        points = [-1, -1, 3, 4, 5, 6, 7, 8]
        user = self._create_user_with_coefficient(8)
        self._create_submits(user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_BETA)
        col_to_index_map = get_col_to_index_map(scoreboard)
        row = get_row_for_user(scoreboard, user)
        self.assertFalse(row.cell_list[col_to_index_map[3]].active)
        for i in range(4, 8):
            self.assertTrue(row.cell_list[col_to_index_map[i]].active)
        self.assertEqual(row.cell_list[col_to_index_map["sum"]].points, "28")

    def test_beta_coeff_9(self):
        points = [-1, -1, 3, 4, 6, 6, 7, 8]
        user = self._create_user_with_coefficient(9)
        self._create_submits(user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_BETA)
        col_to_index_map = get_col_to_index_map(scoreboard)
        row = get_row_for_user(scoreboard, user)
        self.assertFalse(row.cell_list[col_to_index_map[3]].active)
        for i in range(4, 8):
            self.assertTrue(row.cell_list[col_to_index_map[i]].active)
        self.assertEqual(row.cell_list[col_to_index_map["sum"]].points, "26")

    def test_beta_only_user(self):
        points = [-1, -1, 2, 3, 4, 5, 6, 7, 8]
        user = self._create_user_with_coefficient(7)
        self._create_submits(user, points)
        response = self.client.get("%s?single_round=True" % self.url)
        self.assertEqual(response.status_code, 200)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_BETA)
        row_beta = get_row_for_user(scoreboard, user)
        scoreboard = get_scoreboard(response.context["scoreboards"], KMS_ALFA)
        row_alfa = get_row_for_user(scoreboard, user)
        self.assertTrue(row_beta.active)
        self.assertFalse(row_alfa.active)

    def test_alfa_only_user(self):
        points = [1, 2, 3, 4, 5]
        user = self._create_user_with_coefficient(1)
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
        points = [1, 2, 9, 4, 5, 6, 7, 8, 9, 10]
        user = self._create_user_with_coefficient(1)
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
        self.assertEqual(row_alfa.cell_list[col_to_index_map["sum"]].points, "31")


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
            task = Task.objects.create(number=i, name="Test task {}".format(i), round=self.round)
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
