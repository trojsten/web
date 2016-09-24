# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import path

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.utils.translation import activate
from wiki.models import Article, ArticleRevision, URLPath

from trojsten.contests.models import Competition, Round, Semester, Task
from trojsten.people.models import User
from trojsten.utils.test_utils import get_noexisting_id


class ArchiveTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=settings.SITE_ID)

        root_article = Article.objects.create()
        ArticleRevision.objects.create(article=root_article, title="test 1")
        urlpath_root = URLPath.objects.create(site=self.site, article=root_article)
        archive_article = Article.objects.create()
        ArticleRevision.objects.create(article=archive_article, title="test 2")
        URLPath.objects.create(site=self.site, article=archive_article, slug="archiv",
                               parent=urlpath_root)

        self.url = reverse('archive')

    def test_no_competitions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # @ToDo: translations
        self.assertContains(response, "Ešte nie sú žiadne súťaže.")

    def test_no_rounds(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(self.site)
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "Ešte nie sú žiadne kolá.")

    def test_one_year(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(self.site)
        semester = Semester.objects.create(
            number=1, name='Test semester', competition=competition, year=1
        )
        Round.objects.create(number=1, semester=semester, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "1. ročník")
        # @ToDo: translations
        self.assertContains(response, "1. časť")
        # @ToDo: translations
        self.assertContains(response, "1. kolo")
        # @ToDo: translations
        self.assertContains(response, "Zadania a vzoráky")
        # @ToDo: translations
        self.assertContains(response, "Výsledky")

    def test_two_competitions(self):
        competition1 = Competition.objects.create(name='TestCompetition 42')
        competition1.sites.add(self.site)

        response = self.client.get(self.url)
        self.assertContains(response, "TestCompetition 42")
        self.assertNotContains(response, "TestCompetition 47")

        competition2 = Competition.objects.create(name='TestCompetition 47')
        competition2.sites.add(self.site)

        response = self.client.get(self.url)
        self.assertContains(response, "TestCompetition 47")

        semester1 = Semester.objects.create(
            number=42, name='Test semester 42', competition=competition1, year=42
        )
        semester2 = Semester.objects.create(
            number=47, name='Test semester 47', competition=competition2, year=47
        )
        Round.objects.create(number=42, semester=semester1, solutions_visible=True, visible=True)
        Round.objects.create(number=47, semester=semester2, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "42. ročník")
        # @ToDo: translations
        self.assertContains(response, "47. ročník")
        # @ToDo: translations
        self.assertContains(response, "42. časť")
        # @ToDo: translations
        self.assertContains(response, "47. časť")
        # @ToDo: translations
        self.assertContains(response, "42. kolo")
        # @ToDo: translations
        self.assertContains(response, "47. kolo")

    def test_two_years(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(self.site)
        semester1 = Semester.objects.create(
            number=1, name='Test semester 1', competition=competition, year=1
        )
        semester2 = Semester.objects.create(
            number=1, name='Test semester 2', competition=competition, year=2
        )
        Round.objects.create(number=1, semester=semester1, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "1. ročník")
        # @ToDo: translations
        self.assertNotContains(response, "2. ročník")

        Round.objects.create(number=1, semester=semester2, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "2. ročník")

    def test_two_semester(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(self.site)
        semester1 = Semester.objects.create(
            number=1, name='Test semester 1', competition=competition, year=1
        )
        semester2 = Semester.objects.create(
            number=2, name='Test semester 2', competition=competition, year=1
        )
        Round.objects.create(number=1, semester=semester1, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "1. časť")
        # @ToDo: translations
        self.assertNotContains(response, "2. časť")

        Round.objects.create(number=1, semester=semester2, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "2. časť")

    def test_two_rounds(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(self.site)
        semester = Semester.objects.create(
            number=1, name='Test semester 1', competition=competition, year=1
        )
        Round.objects.create(number=1, semester=semester, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "1. kolo")
        # @ToDo: translations
        self.assertNotContains(response, "2. kolo")

        Round.objects.create(number=2, semester=semester, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "2. kolo")

    def test_invisible_rounds(self):
        group = Group.objects.create(name="Test Group")
        competition = Competition.objects.create(name='TestCompetition', organizers_group=group)
        competition.sites.add(self.site)
        semester = Semester.objects.create(
            number=1, name='Test semester 1', competition=competition, year=1
        )
        Round.objects.create(number=1, semester=semester, solutions_visible=True, visible=False)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertNotContains(response, "1. kolo")

        user = User.objects.create_user(username="TestUser", password="password",
                                        first_name="Arasid", last_name="Mrkvicka", graduation=2014)
        group.user_set.add(user)
        self.client.force_login(user)
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "1. kolo")
        # @ToDo: translations
        self.assertContains(response, "skryté")


class RoundMethodTests(TestCase):
    def test_get_pdf_name(self):
        c = Competition.objects.create(name='ABCD')
        s = Semester.objects.create(year=47, competition=c, number=1)
        r = Round.objects.create(number=3, semester=s, visible=True, solutions_visible=True)
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
        semester = Semester.objects.create(
            number=1, name='Test semester', competition=competition, year=1
        )
        self.round = Round.objects.create(number=1, semester=semester, visible=True,
                                          solutions_visible=True)
        self.invisible_round = Round.objects.create(number=1, semester=semester, visible=False,
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

    def test_staff_invisible_round(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.invisible_round_url)
        self.assertEqual(response.status_code, 200)

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
        semester = Semester.objects.create(
            number=1, name='Test semester', competition=competition, year=1
        )
        self.round = Round.objects.create(number=1, semester=semester, visible=True,
                                          solutions_visible=True)
        self.invisible_round = Round.objects.create(number=1, semester=semester, visible=False,
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

    def test_staff_invisible_round(self):
        self.client.force_login(self.staff_user)
        task = Task.objects.create(number=1, name='Test task', round=self.invisible_round)
        url = reverse('task_statement', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse('solution_statement', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_statement(self):
        response = self.client.get(self.task_url)
        self.assertContains(response, 'Test task')
        self.assertContains(response, 'test <b>html</b> task statement')
        response = self.client.get(self.solution_url)
        self.assertContains(response, 'Test task')
        self.assertContains(response, 'test <b>html</b> solution statement')
        self.assertContains(response, 'test <b>html</b> task statement')

    def test_statement_logged_in(self):
        self.client.force_login(self.nonstaff_user)
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
        self.semester = Semester.objects.create(
            number=1, name='Test semester', competition=competition, year=1,
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
            number=1, semester=self.semester, visible=True, solutions_visible=True,
        )
        url = reverse('view_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_solution_pdf(self):
        round = Round.objects.create(
            number=1, semester=self.semester, visible=True, solutions_visible=True,
        )
        url = reverse('view_solutions_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_missing_task_pdf(self):
        round2 = Round.objects.create(
            number=2, semester=self.semester, visible=True, solutions_visible=True,
        )
        url = reverse('view_pdf', kwargs={'round_id': round2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_missing_solutions_pdf(self):
        round2 = Round.objects.create(
            number=2, semester=self.semester, visible=True, solutions_visible=True,
        )
        url = reverse('view_solutions_pdf', kwargs={'round_id': round2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invisible_task_pdf(self):
        round = Round.objects.create(
            number=1, semester=self.semester, visible=False, solutions_visible=False,
        )
        url = reverse('view_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invisible_solution_pdf(self):
        round = Round.objects.create(
            number=1, semester=self.semester, visible=True, solutions_visible=False,
        )
        url = reverse('view_solutions_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_nostaff_invisible_task_pdf(self):
        self.client.force_login(self.nonstaff_user)
        round = Round.objects.create(
            number=1, semester=self.semester, visible=False, solutions_visible=False,
        )
        url = reverse('view_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_nostaff_invisible_solution_pdf(self):
        self.client.force_login(self.nonstaff_user)
        round = Round.objects.create(
            number=1, semester=self.semester, visible=True, solutions_visible=False,
        )
        url = reverse('view_solutions_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_invisible_task_pdf(self):
        self.client.force_login(self.staff_user)
        round = Round.objects.create(
            number=1, semester=self.semester, visible=False, solutions_visible=False,
        )
        url = reverse('view_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_staff_invisible_solution_pdf(self):
        self.client.force_login(self.staff_user)
        round = Round.objects.create(
            number=1, semester=self.semester, visible=True, solutions_visible=False,
        )
        url = reverse('view_solutions_pdf', kwargs={'round_id': round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
