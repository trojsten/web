# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from trojsten.contests.models import Competition, Round, Semester, Task
from trojsten.people.models import User, UserPropertyKey
from trojsten.rules.test import get_row_for_user
from trojsten.schools.models import School
from trojsten.submit.models import Submit
from trojsten.utils.test_utils import get_noexisting_id

from .representation import Results, ResultsCell, ResultsCol, ResultsRow


class RecentResultsTest(TestCase):
    def setUp(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.semester = Semester.objects.create(number=1, name='Test semester', competition=competition,
                                                year=1)
        self.url = reverse('view_latest_results')
        self.year = timezone.now().year + 2
        self.user = User.objects.create(username="TestUser", password="password",
                                        first_name="Jozko", last_name="Mrkvicka", graduation=self.year)

    def test_no_rounds(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # @ToDo: translations
        self.assertContains(response, 'Ešte nebeží žiadne kolo.')

    def test_rounds(self):
        start1 = timezone.now() + timezone.timedelta(-8)
        end1 = timezone.now() + timezone.timedelta(-4)
        start2 = timezone.now() + timezone.timedelta(-4)
        end2 = timezone.now() + timezone.timedelta(4)
        round1 = Round.objects.create(number=1, semester=self.semester, visible=True,
                                      solutions_visible=True, start_time=start1, end_time=end1)
        round2 = Round.objects.create(number=2, semester=self.semester, visible=True, start_time=start2,
                                      end_time=end2, solutions_visible=True)
        task1 = Task.objects.create(number=1, name='Test task 1', round=round1)
        task2 = Task.objects.create(number=1, name='Test task 2', round=round2)

        submit = Submit.objects.create(task=task1, user=self.user, submit_type=0, points=5)
        submit.time = start1 + timezone.timedelta(0, 5)
        submit.save()

        response = self.client.get("%s?single_round=True" % self.url)
        self.assertNotContains(response, self.user.get_full_name())
        # @ToDo: translations
        self.assertContains(response, 'Žiadne submity')

        submit = Submit.objects.create(task=task2, user=self.user, submit_type=0, points=5)
        submit.time = start2 + timezone.timedelta(0, 5)
        submit.save()

        response = self.client.get("%s?single_round=True" % self.url)
        self.assertContains(response, self.user.get_full_name())

    def test_old_user(self):
        old_user = User.objects.create(username="TestOldUser", password="password",
                                       first_name="Jozko", last_name="Starcek", graduation=2010)
        start = timezone.now() + timezone.timedelta(-4)
        end = timezone.now() + timezone.timedelta(4)
        test_round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                          solutions_visible=True, start_time=start, end_time=end)
        task = Task.objects.create(number=1, name='Test task 1', round=test_round)

        submit = Submit.objects.create(task=task, user=old_user, submit_type=0, points=5)
        submit.time = start + timezone.timedelta(0, 5)
        submit.save()

        response = self.client.get(self.url)
        self.assertNotContains(response, old_user.get_full_name())

        response = self.client.get("%s?show_staff=True" % self.url)
        self.assertContains(response, old_user.get_full_name())

    def test_ignored_user(self):
        user = User.objects.create(username="TestIgnoredUser", password="password",
                                   first_name="Jozko", last_name="Starcek", graduation=self.year)
        user.ignored_competitions.add(self.semester.competition)
        start = timezone.now() + timezone.timedelta(-4)
        end = timezone.now() + timezone.timedelta(4)
        test_round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                          solutions_visible=True, start_time=start, end_time=end)
        task = Task.objects.create(number=1, name='Test task 1', round=test_round)

        submit = Submit.objects.create(task=task, user=user, submit_type=0, points=5)
        submit.time = start + timezone.timedelta(0, 5)
        submit.save()

        response = self.client.get(self.url)
        self.assertNotContains(response, user.get_full_name())

        response = self.client.get("%s?show_staff=True" % self.url)
        self.assertContains(response, user.get_full_name())

    def test_invalid_user(self):
        test_prop_key = UserPropertyKey.objects.create(key_name='Test property')
        self.semester.competition.required_user_props.add(test_prop_key)
        start = timezone.now() + timezone.timedelta(-4)
        end = timezone.now() + timezone.timedelta(4)
        test_round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                          solutions_visible=True, start_time=start, end_time=end)
        task = Task.objects.create(number=1, name='Test task 1', round=test_round)

        submit = Submit.objects.create(task=task, user=self.user, submit_type=0, points=5)
        submit.time = start + timezone.timedelta(0, 5)
        submit.save()

        response = self.client.get(self.url)
        self.assertNotContains(response, self.user.get_full_name())

        response = self.client.get("%s?show_staff=True" % self.url)
        self.assertContains(response, self.user.get_full_name())

    def test_dont_show_old_result(self):
        bad_time = timezone.now() + timezone.timedelta(days=-200)
        competition1 = Competition.objects.create(name='oldCompetition')
        competition1.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester1 = Semester.objects.create(
            number=1, name='Test semester', competition=competition1, year=1
        )
        Round.objects.create(number=1, semester=semester1, solutions_visible=True, visible=True,
                             end_time=bad_time)

        good_time = timezone.now() + timezone.timedelta(days=-147)
        competition2 = Competition.objects.create(name='newCompetition')
        competition2.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester2 = Semester.objects.create(
            number=1, name='Test semester', competition=competition2, year=1
        )
        Round.objects.create(number=2, semester=semester2, solutions_visible=True, visible=True,
                             end_time=good_time)

        response = self.client.get(self.url)

        competition_names = list(map(lambda x: x.scoreboard.round.semester.competition.name,
                                     response.context['scoreboards']))
        self.assertIn('newCompetition', competition_names)
        self.assertNotIn('oldCompetition', competition_names)


class ResultsTest(TestCase):
    def setUp(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.semester0 = Semester.objects.create(number=1, name='Test semester 2', year=0,
                                                 competition=competition)
        self.semester1 = Semester.objects.create(number=1, name='Test semester 1', year=1,
                                                 competition=competition)
        self.semester2 = Semester.objects.create(number=2, name='Test semester 2', year=1,
                                                 competition=competition)

        start0 = timezone.now() + timezone.timedelta(days=-47 - 366)
        end0 = timezone.now() + timezone.timedelta(days=-366)
        start1 = timezone.now() + timezone.timedelta(-12)
        end1 = timezone.now() + timezone.timedelta(-8)
        start2 = timezone.now() + timezone.timedelta(-8)
        end2 = timezone.now() + timezone.timedelta(-4)
        start3 = timezone.now() + timezone.timedelta(-4)
        end3 = timezone.now() + timezone.timedelta(4)
        self.round0 = Round.objects.create(number=2, semester=self.semester0, solutions_visible=True,
                                           start_time=start0, end_time=end0, visible=True)
        self.round1 = Round.objects.create(number=1, semester=self.semester1, solutions_visible=True,
                                           start_time=start1, end_time=end1, visible=True)
        self.round2 = Round.objects.create(number=2, semester=self.semester1, solutions_visible=True,
                                           start_time=start2, end_time=end2, visible=True)
        self.round3 = Round.objects.create(number=2, semester=self.semester2, solutions_visible=True,
                                           start_time=start3, end_time=end3, visible=True)
        self.task0 = Task.objects.create(number=1, name='Test task 0', round=self.round0)
        self.task1 = Task.objects.create(number=1, name='Test task 1', round=self.round1)
        self.task2 = Task.objects.create(number=1, name='Test task 2', round=self.round2)
        self.task3 = Task.objects.create(number=1, name='Test task 3', round=self.round3)

        year = timezone.now().year + 2
        self.user = User.objects.create(username="TestUser", password="password",
                                        first_name="Jozko", last_name="Mrkvicka", graduation=year)
        self.url0 = reverse('view_results', kwargs={'round_id': self.round0.id})
        self.url1 = reverse('view_results', kwargs={'round_id': self.round1.id})
        self.url2 = reverse('view_results', kwargs={'round_id': self.round2.id})
        self.url3 = reverse('view_results', kwargs={'round_id': self.round3.id})

    def test_invalid_round(self):
        url = reverse('view_results', kwargs={'round_id': get_noexisting_id(Round)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_one_round_no_users(self):
        response = self.client.get(self.url1)
        # @ToDo: translations
        self.assertContains(response, 'Žiadne submity')

    def test_submit_only_first_round(self):
        submit_time = self.round1.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task1, user=self.user, submit_type=0, points=5)
        submit.time = submit_time
        submit.save()
        response = self.client.get(self.url1)
        self.assertContains(response, self.user.get_full_name())
        response = self.client.get(self.url2)
        self.assertContains(response, self.user.get_full_name())
        response = self.client.get(self.url3)
        self.assertNotContains(response, self.user.get_full_name())

    def test_submit_only_second_round(self):
        submit_time = self.round2.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task2, user=self.user, submit_type=0, points=5)
        submit.time = submit_time
        submit.save()
        response = self.client.get(self.url1)
        self.assertNotContains(response, self.user.get_full_name())
        response = self.client.get(self.url2)
        self.assertContains(response, self.user.get_full_name())
        response = self.client.get(self.url3)
        self.assertNotContains(response, self.user.get_full_name())

    def test_submit_all(self):
        submit_time = self.round1.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task1, user=self.user, submit_type=0, points=5)
        submit.time = submit_time
        submit.save()

        submit_time = self.round2.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task2, user=self.user, submit_type=0, points=5)
        submit.time = submit_time
        submit.save()

        submit_time = self.round3.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task3, user=self.user, submit_type=0, points=5)
        submit.time = submit_time
        submit.save()

        response = self.client.get(self.url1)
        self.assertContains(response, self.user.get_full_name())
        response = self.client.get(self.url2)
        self.assertContains(response, self.user.get_full_name())
        response = self.client.get(self.url3)
        self.assertContains(response, self.user.get_full_name())

    def test_old_user(self):
        old_user = User.objects.create(username="TestOldUser", password="password",
                                       first_name="Jozko", last_name="Starcek", graduation=2010)
        submit = Submit.objects.create(task=self.task1, user=old_user, submit_type=0, points=5)
        submit.time = self.round1.start_time + timezone.timedelta(0, 5)
        submit.save()

        response = self.client.get(self.url1)
        self.assertNotContains(response, old_user.get_full_name())

        response = self.client.get("%s?show_staff=True" % self.url1)
        self.assertContains(response, old_user.get_full_name())

    def test_single_round(self):
        submit_time = self.round1.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task1, user=self.user, submit_type=0, points=5)
        submit.time = submit_time
        submit.save()
        response = self.client.get("%s?single_round=True" % self.url2)
        self.assertNotContains(response, self.user.get_full_name())

        submit = Submit.objects.create(task=self.task2, user=self.user, submit_type=0, points=5)
        submit.time = self.round2.start_time + timezone.timedelta(0, 5)
        submit.save()
        response = self.client.get("%s?single_round=True" % self.url2)
        self.assertContains(response, self.user.get_full_name())

    def test_use_correct_year_in_old_results(self):
        submit_time = self.round0.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task0, user=self.user, submit_type=0, points=9)
        submit.time = submit_time
        submit.save()

        submit_time = self.round1.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task1, user=self.user, submit_type=0, points=9)
        submit.time = submit_time
        submit.save()

        response = self.client.get(self.url0)
        for scoreboard_object in response.context['scoreboards']:
            scoreboard = scoreboard_object.scoreboard
            row = get_row_for_user(scoreboard, self.user)
            self.assertEqual(row.user.year, self.user.school_year_at(self.round0.end_time))

        response = self.client.get(self.url1)
        for scoreboard_object in response.context['scoreboards']:
            scoreboard = scoreboard_object.scoreboard
            row = get_row_for_user(scoreboard, self.user)
            self.assertEqual(row.user.year, self.user.school_year_at(self.round1.end_time))


class SerializationTest(TestCase):
    def test_serialize_cell(self):
        d = {
            'points': 15,
            'manual_points': 10,
            'auto_points': 5,
            'active': True
        }
        cell = ResultsCell(15, 10, 5, True)

        self.assertDictEqual(cell.serialize(), d)

    def test_serialize_col_with_task(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(number=1, name='Test semester', competition=competition,
                                           year=1)
        rnd = Round.objects.create(number=1, semester=semester, visible=True,
                                   solutions_visible=True, start_time=timezone.now(),
                                   end_time=timezone.now() + timezone.timedelta(4))
        task = Task.objects.create(number=1, name='Test task 1', round=rnd)
        d = {
            'name': '1',
            'key': 'T1',
            'task': {'id': task.id, 'name': 'Test task 1'}
        }
        col = ResultsCol('T1', '1', task)

        self.assertDictEqual(col.serialize(), d)

    def test_serialize_col_without_task(self):
        d = {
            'name': '1',
            'key': 'T1',
        }
        col = ResultsCol('T1', '1')

        self.assertDictEqual(col.serialize(), d)

    def test_serialize_row_without_previous(self):
        school = School.objects.create(abbreviation='GJH', verbose_name='Gymnazium Jura Hronca')
        user = User.objects.create(username="TestUser", password="password",
                                   first_name="Jozko", last_name="Mrkvicka",
                                   graduation=timezone.now().year + 2,
                                   school=school)

        school_dict = {
            'id': school.id,
            'name': 'GJH',
            'verbose_name': 'Gymnazium Jura Hronca',
        }
        user_dict = {
            'id': user.id,
            'username': 'TestUser',
            'name': 'Jozko Mrkvicka',
            'year': user.school_year,
            'school': school_dict,
        }
        cell1 = ResultsCell(15, 10, 5, True)
        cell2 = ResultsCell(10, 6, 4, False)
        cell_list_raw = [cell1, cell2]
        cell_list = [cell.serialize() for cell in cell_list_raw]
        d = {
            'user': user_dict,
            'cell_list': cell_list,
            'rank': 1,
            'active': True,
        }
        row = ResultsRow(user, active=True)
        row.cell_list = cell_list
        row.rank = 1

        self.assertDictEqual(row.serialize(), d)

    def test_serialize_row_with_previous(self):
        school = School.objects.create(abbreviation='GJH', verbose_name='Gymnazium Jura Hronca')
        user = User.objects.create(username="TestUser", password="password",
                                   first_name="Jozko", last_name="Mrkvicka",
                                   graduation=timezone.now().year + 2,
                                   school=school)

        school_dict = {
            'id': school.id,
            'name': 'GJH',
            'verbose_name': 'Gymnazium Jura Hronca',
        }
        user_dict = {
            'id': user.id,
            'username': 'TestUser',
            'name': 'Jozko Mrkvicka',
            'year': user.school_year,
            'school': school_dict,
        }
        cell1 = ResultsCell(15, 10, 5, True)
        cell2 = ResultsCell(10, 6, 4, False)
        cell3 = ResultsCell(11, 6, 5, True)
        cell_list_raw = [cell1, cell2]
        cell_list = [cell.serialize() for cell in cell_list_raw]
        prev_cell_list_raw = [cell3]
        prev_cell_list = [cell.serialize() for cell in prev_cell_list_raw]
        prev_d = {
            'user': user_dict,
            'cell_list': prev_cell_list,
            'rank': 2,
            'active': True,
        }
        d = {
            'user': user_dict,
            'cell_list': cell_list,
            'rank': 1,
            'previous': prev_d,
            'active': True,
        }
        prev_row = ResultsRow(user, active=True)
        prev_row.cell_list = prev_cell_list_raw
        prev_row.rank = 2
        row = ResultsRow(user, previous=prev_row, active=True)
        row.cell_list = cell_list_raw
        row.rank = 1

        self.assertDictEqual(row.serialize(), d)

    def test_serialize_results(self):
        col_d = {
            'name': '1',
            'key': 'T1',
        }
        col = ResultsCol('T1', '1')

        school = School.objects.create(abbreviation='GJH', verbose_name='Gymnazium Jura Hronca')
        user = User.objects.create(username="TestUser", password="password",
                                   first_name="Jozko", last_name="Mrkvicka",
                                   graduation=timezone.now().year + 2,
                                   school=school)

        school_dict = {
            'id': school.id,
            'name': 'GJH',
            'verbose_name': 'Gymnazium Jura Hronca',
        }
        user_dict = {
            'id': user.id,
            'username': 'TestUser',
            'name': 'Jozko Mrkvicka',
            'year': user.school_year,
            'school': school_dict,
        }
        cell1 = ResultsCell(15, 10, 5, True)
        cell2 = ResultsCell(10, 6, 4, False)
        cell_list_raw = [cell1, cell2]
        cell_list = [cell.serialize() for cell in cell_list_raw]
        row1_d = {
            'user': user_dict,
            'cell_list': cell_list,
            'rank': 1,
            'active': True,
        }
        row1 = ResultsRow(user, active=True)
        row1.cell_list = cell_list
        row1.rank = 1

        user = User.objects.create(username="TestUser2", password="password",
                                   first_name="Ferko", last_name="Mrkvicka",
                                   graduation=timezone.now().year + 3,
                                   school=school)

        user_dict = {
            'id': user.id,
            'username': 'TestUser2',
            'name': 'Ferko Mrkvicka',
            'year': user.school_year,
            'school': school_dict,
        }
        cell1 = ResultsCell(15, 10, 5, True)
        cell2 = ResultsCell(10, 6, 4, False)
        cell_list_raw = [cell1, cell2]
        cell_list = [cell.serialize() for cell in cell_list_raw]
        row2_d = {
            'user': user_dict,
            'cell_list': cell_list,
            'rank': 2,
            'active': True,
        }
        row2 = ResultsRow(user, active=True)
        row2.cell_list = cell_list
        row2.rank = 2

        d = {
            'cols': [col_d],
            'rows': [row1_d, row2_d]
        }
        results = Results(None)
        results.cols = [col]
        results.rows = [row1, row2]
        self.assertDictEqual(results.serialize(), d)
