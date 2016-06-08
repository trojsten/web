# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import path

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.utils.translation import activate

from trojsten.contests.models import Competition, Round, Series, Task
from trojsten.people.models import User
from trojsten.utils.test_utils import get_noexisting_id


class RoundMethodTests(TestCase):
    def test_get_pdf_name(self):
        c = Competition.objects.create(name='ABCD')
        s = Series.objects.create(year=47, competition=c, number=1)
        r = Round.objects.create(number=3, series=s, visible=True, solutions_visible=True)
        activate('en')
        self.assertEqual(r.get_pdf_name(), u'ABCD-year47-round3-tasks.pdf')
        self.assertEqual(r.get_pdf_name(True), u'ABCD-year47-round3-solutions.pdf')
        activate('sk')
        self.assertEqual(r.get_pdf_name(), u'ABCD-rocnik47-kolo3-zadania.pdf')
        self.assertEqual(r.get_pdf_name(True), u'ABCD-rocnik47-kolo3-vzoraky.pdf')


class TaskListTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name='staff')
        competition = Competition.objects.create(name='TestCompetition', organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series', competition=competition,
                                       year=1)
        self.round = Round.objects.create(number=1, series=series, visible=True,
                                          solutions_visible=True)
        self.invisible_round = Round.objects.create(number=1, series=series, visible=False,
                                                    solutions_visible=False)
        self.staff_user = User.objects.create(username='staff')
        self.staff_user.groups.add(group)
        self.nonstaff_user = User.objects.create(username='nonstaff')
        self.url = reverse('task_list', kwargs={'round_id': self.round.id})
        self.invisible_round_url = reverse(
            'task_list', kwargs={'round_id': self.invisible_round.id}
        )

    def test_invalid_round(self):
        url = reverse('task_list', kwargs={'round_id': get_noexisting_id(Round)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invisible_round(self):
        response = self.client.get(self.invisible_round_url)
        self.assertEqual(response.status_code, 404)

    def test_nonstaff_invisible_round(self):
        self.client.force_login(self.nonstaff_user)
        response = self.client.get(self.invisible_round_url)
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_staff_invisible_round(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.invisible_round_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_no_tasks(self):
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, 'Žiadne úlohy')

    def test_visible_tasks(self):
        Task.objects.create(number=1, name='Test task', round=self.round)
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, 'Test task')


@override_settings(
    TASK_STATEMENTS_PATH=path.join(path.dirname(__file__), 'test_data', 'statements'),
    TASK_STATEMENTS_SUFFIX_YEAR='',
    TASK_STATEMENTS_SUFFIX_ROUND='',
    TASK_STATEMENTS_TASKS_DIR='tasks',
    TASK_STATEMENTS_PREFIX_TASK='',
    TASK_STATEMENTS_SOLUTIONS_DIR='solutions',
    TASK_STATEMENTS_HTML_DIR='html',
)
class TaskAndSolutionStatementsTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name='staff')
        competition = Competition.objects.create(name='TestCompetition', organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series', competition=competition,
                                       year=1)
        self.round = Round.objects.create(number=1, series=series, visible=True,
                                          solutions_visible=True)
        self.invisible_round = Round.objects.create(number=1, series=series, visible=False,
                                                    solutions_visible=False)
        self.task = Task.objects.create(number=1, name='Test task', round=self.round)
        self.staff_user = User.objects.create(username='staff')
        self.staff_user.groups.add(group)
        self.nonstaff_user = User.objects.create(username='nonstaff')
        self.task_url = reverse('task_statement', kwargs={'task_id': self.task.id})
        self.solution_url = reverse('solution_statement', kwargs={'task_id': self.task.id})

    def test_invalid_task(self):
        url = reverse('task_statement', kwargs={'task_id': get_noexisting_id(Task)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        url = reverse('solution_statement', kwargs={'task_id': get_noexisting_id(Task)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invisible_round(self):
        task = Task.objects.create(number=1, name='Test task', round=self.invisible_round)
        url = reverse('task_statement', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        url = reverse('solution_statement', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_nonstaff_invisible_round(self):
        self.client.force_login(self.nonstaff_user)
        task = Task.objects.create(number=1, name='Test task', round=self.invisible_round)
        url = reverse('task_statement', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        url = reverse('solution_statement', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_staff_invisible_round(self):
        self.client.force_login(self.staff_user)
        task = Task.objects.create(number=1, name='Test task', round=self.invisible_round)
        url = reverse('task_statement', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse('solution_statement', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_statement(self):
        response = self.client.get(self.task_url)
        self.assertContains(response, 'Test task')
        self.assertContains(response, 'test <b>html</b> task statement')
        response = self.client.get(self.solution_url)
        self.assertContains(response, 'Test task')
        self.assertContains(response, 'test <b>html</b> solution statement')
        self.assertContains(response, 'test <b>html</b> task statement')

    def test_missing_task_statement_file(self):
        task = Task.objects.create(number=3, name='Test task 3', round=self.round)
        url = reverse('task_statement', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertContains(response, 'Test task 3')
        url = reverse('solution_statement', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertContains(response, 'Test task 3')
        self.assertContains(response, 'test <b>html</b> solution statement')

    def test_missing_solution_statement_file(self):
        task = Task.objects.create(number=2, name='Test task 2', round=self.round)
        url = reverse('solution_statement', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertContains(response, 'Test task 2')
        self.assertContains(response, 'test <b>html</b> task statement')


@override_settings(
    TASK_STATEMENTS_PATH=path.join(path.dirname(__file__), 'test_data', 'statements'),
    TASK_STATEMENTS_SUFFIX_YEAR='',
    TASK_STATEMENTS_SUFFIX_ROUND='',
    TASK_STATEMENTS_TASKS_DIR='tasks',
    TASK_STATEMENTS_PREFIX_TASK='',
    TASK_STATEMENTS_SOLUTIONS_DIR='solutions',
    TASK_STATEMENTS_PDF='tasks.pdf',
    TASK_STATEMENTS_SOLUTIONS_PDF='solutions.pdf',
)
class PdfDownloadTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name='staff')
        competition = Competition.objects.create(name='TestCompetition', organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.series = Series.objects.create(
            number=1, name='Test series', competition=competition, year=1,
        )
        self.staff_user = User.objects.create(username='staff')
        self.staff_user.groups.add(group)
        self.nonstaff_user = User.objects.create(username='nonstaff')

    def test_invalid_task_pdf(self):
        url = reverse('view_pdf', kwargs={'round_id': get_noexisting_id(Round)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_solutions_pdf(self):
        url = reverse('view_solutions_pdf', kwargs={'round_id': get_noexisting_id(Round)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_task_pdf(self):
        round = Round.objects.create(
            number=1, series=self.series, visible=True, solutions_visible=True,
        )
        url = reverse('view_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_solution_pdf(self):
        round = Round.objects.create(
            number=1, series=self.series, visible=True, solutions_visible=True,
        )
        url = reverse('view_solutions_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_missing_task_pdf(self):
        round2 = Round.objects.create(
            number=2, series=self.series, visible=True, solutions_visible=True,
        )
        url = reverse('view_pdf', kwargs={'round_id': round2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_missing_solutions_pdf(self):
        round2 = Round.objects.create(
            number=2, series=self.series, visible=True, solutions_visible=True,
        )
        url = reverse('view_solutions_pdf', kwargs={'round_id': round2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invisible_task_pdf(self):
        round = Round.objects.create(
            number=1, series=self.series, visible=False, solutions_visible=False,
        )
        url = reverse('view_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invisible_solution_pdf(self):
        round = Round.objects.create(
            number=1, series=self.series, visible=True, solutions_visible=False,
        )
        url = reverse('view_solutions_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_nostaff_invisible_task_pdf(self):
        self.client.force_login(self.nonstaff_user)
        round = Round.objects.create(
            number=1, series=self.series, visible=False, solutions_visible=False,
        )
        url = reverse('view_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_nostaff_invisible_solution_pdf(self):
        self.client.force_login(self.nonstaff_user)
        round = Round.objects.create(
            number=1, series=self.series, visible=True, solutions_visible=False,
        )
        url = reverse('view_solutions_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_staff_invisible_task_pdf(self):
        self.client.force_login(self.staff_user)
        round = Round.objects.create(
            number=1, series=self.series, visible=False, solutions_visible=False,
        )
        url = reverse('view_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_staff_invisible_solution_pdf(self):
        self.client.force_login(self.staff_user)
        round = Round.objects.create(
            number=1, series=self.series, visible=True, solutions_visible=False,
        )
        url = reverse('view_solutions_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
