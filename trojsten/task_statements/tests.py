# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import path

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from trojsten.contests.models import Competition, Round, Series
from trojsten.tasks.models import Task


class TaskListTests(TestCase):
    def setUp(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series', competition=competition,
                                       year=1)
        self.round = Round.objects.create(number=1, series=series, visible=True,
                                          solutions_visible=True)
        self.url = reverse('task_list', kwargs={'round_id': self.round.id})

    def test_invalid_round(self):
        url = reverse('task_list', kwargs={'round_id': 47})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

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
class TaskStatementsTests(TestCase):
    def setUp(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series', competition=competition,
                                       year=1)
        self.round = Round.objects.create(number=1, series=series, visible=True,
                                          solutions_visible=True)
        self.task = Task.objects.create(number=1, name='Test task', round=self.round)
        self.url = reverse('task_statement', kwargs={'task_id': self.task.id})

    def test_invalid_task(self):
        url = reverse('task_statement', kwargs={'task_id': 47})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_task_statement(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Test task')
        self.assertContains(response, 'test <b>html</b> task statement')

    def test_missing_task_statement_file(self):
        task = Task.objects.create(number=3, name='Test task 3', round=self.round)
        url = reverse('task_statement', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertContains(response, 'Test task 3')


@override_settings(
    TASK_STATEMENTS_PATH=path.join(path.dirname(__file__), 'test_data', 'statements'),
    TASK_STATEMENTS_SUFFIX_YEAR='',
    TASK_STATEMENTS_SUFFIX_ROUND='',
    TASK_STATEMENTS_TASKS_DIR='tasks',
    TASK_STATEMENTS_PREFIX_TASK='',
    TASK_STATEMENTS_SOLUTIONS_DIR='solutions',
    TASK_STATEMENTS_HTML_DIR='html',
)
class SolutionStatementsTests(TestCase):
    def setUp(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series', competition=competition,
                                       year=1)
        self.round = Round.objects.create(number=1, series=series, visible=True,
                                          solutions_visible=True)
        self.task = Task.objects.create(number=1, name='Test task', round=self.round)
        self.url = reverse('solution_statement', kwargs={'task_id': self.task.id})

    def test_invalid_task(self):
        url = reverse('solution_statement', kwargs={'task_id': 47})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_solution_statement(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Test task')
        self.assertContains(response, 'test <b>html</b> solution statement')
        self.assertContains(response, 'test <b>html</b> task statement')

    def test_missing_task_statement_file(self):
        task = Task.objects.create(number=3, name='Test task 3', round=self.round)
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
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(
            number=1, name='Test series', competition=competition, year=1,
        )
        self.round = Round.objects.create(
            number=1, series=series, visible=True, solutions_visible=True,
        )

    def test_invalid_task_pdf(self):
        url = reverse('view_pdf', kwargs={'round_id': 47})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_solutions_pdf(self):
        url = reverse('view_solutions_pdf', kwargs={'round_id': 47})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_task_pdf(self):
        url = reverse('view_pdf', kwargs={'round_id': self.round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_solution_pdf(self):
        url = reverse('view_solutions_pdf', kwargs={'round_id': self.round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
