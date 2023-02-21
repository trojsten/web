# -*- coding: utf-8 -*-
from os import path

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.files.storage import FileSystemStorage
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from news.models import Entry as NewsEntry
from wiki.models import Article, ArticleRevision, URLPath

import trojsten.submit.constants as submit_constants
from trojsten.contests import constants
from trojsten.contests.models import Competition, Round, Semester, Task
from trojsten.notifications.models import Notification
from trojsten.people.models import User
from trojsten.rules.susi_constants import SUSI_COMPETITION_ID
from trojsten.submit.models import Submit
from trojsten.utils.test_utils import TestNonFileSystemStorage, get_noexisting_id


class ArchiveTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=settings.SITE_ID)

        root_article = Article.objects.create()
        ArticleRevision.objects.create(article=root_article, title="test 1")
        urlpath_root = URLPath.objects.create(site=self.site, article=root_article)
        archive_article = Article.objects.create()
        ArticleRevision.objects.create(article=archive_article, title="test 2")
        URLPath.objects.create(
            site=self.site, article=archive_article, slug="archiv", parent=urlpath_root
        )

        self.url = reverse("archive")

    def test_no_competitions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # @ToDo: translations
        self.assertContains(response, "Ešte nie sú žiadne súťaže.")

    def test_no_rounds(self):
        competition = Competition.objects.create(name="TestCompetition")
        competition.sites.add(self.site)
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "Ešte nie sú žiadne kolá.")

    def test_one_year(self):
        competition = Competition.objects.create(name="TestCompetition")
        competition.sites.add(self.site)
        semester = Semester.objects.create(
            number=1, name="Test semester", competition=competition, year=1
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
        competition1 = Competition.objects.create(name="TestCompetition 42")
        competition1.sites.add(self.site)

        response = self.client.get(self.url)
        self.assertContains(response, "TestCompetition 42")
        self.assertNotContains(response, "TestCompetition 47")

        competition2 = Competition.objects.create(name="TestCompetition 47")
        competition2.sites.add(self.site)

        response = self.client.get(self.url)
        self.assertContains(response, "TestCompetition 47")

        semester1 = Semester.objects.create(
            number=42, name="Test semester 42", competition=competition1, year=42
        )
        semester2 = Semester.objects.create(
            number=47, name="Test semester 47", competition=competition2, year=47
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
        competition = Competition.objects.create(name="TestCompetition")
        competition.sites.add(self.site)
        semester1 = Semester.objects.create(
            number=1, name="Test semester 1", competition=competition, year=1
        )
        semester2 = Semester.objects.create(
            number=1, name="Test semester 2", competition=competition, year=2
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
        competition = Competition.objects.create(name="TestCompetition")
        competition.sites.add(self.site)
        semester1 = Semester.objects.create(
            number=1, name="Test semester 1", competition=competition, year=1
        )
        semester2 = Semester.objects.create(
            number=2, name="Test semester 2", competition=competition, year=1
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
        competition = Competition.objects.create(name="TestCompetition")
        competition.sites.add(self.site)
        semester = Semester.objects.create(
            number=1, name="Test semester 1", competition=competition, year=1
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
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(self.site)
        semester = Semester.objects.create(
            number=1, name="Test semester 1", competition=competition, year=1
        )
        Round.objects.create(number=1, semester=semester, solutions_visible=True, visible=False)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertNotContains(response, "1. kolo")

        user = User.objects.create_user(
            username="TestUser",
            password="password",
            first_name="Arasid",
            last_name="Mrkvicka",
            graduation=2014,
        )
        group.user_set.add(user)
        self.client.force_login(user)
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "1. kolo")
        # @ToDo: translations
        self.assertContains(response, "skryté")


class RoundMethodTests(TestCase):
    def test_get_pdf_name(self):
        c = Competition.objects.create(name="ABCD")
        s = Semester.objects.create(year=47, competition=c, number=1)
        r = Round.objects.create(number=3, semester=s, visible=True, solutions_visible=True)
        activate("en")
        self.assertEqual(r.get_pdf_name(), "ABCD-year47-round3-tasks.pdf")
        self.assertEqual(r.get_pdf_name(True), "ABCD-year47-round3-solutions.pdf")
        activate("sk")
        self.assertEqual(r.get_pdf_name(), "ABCD-rocnik47-kolo3-zadania.pdf")
        self.assertEqual(r.get_pdf_name(True), "ABCD-rocnik47-kolo3-vzoraky.pdf")


class TaskListTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name="staff")
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(
            number=1, name="Test semester", competition=competition, year=1
        )
        self.round = Round.objects.create(
            number=1, semester=semester, visible=True, solutions_visible=True
        )
        self.invisible_round = Round.objects.create(
            number=1, semester=semester, visible=False, solutions_visible=False
        )
        self.staff_user = User.objects.create(username="staff")
        self.staff_user.groups.add(group)
        self.nonstaff_user = User.objects.create(username="nonstaff")
        self.url = reverse("task_list", kwargs={"round_id": self.round.id})
        self.invisible_round_url = reverse(
            "task_list", kwargs={"round_id": self.invisible_round.id}
        )

    def test_invalid_round(self):
        url = reverse("task_list", kwargs={"round_id": get_noexisting_id(Round)})
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
        self.assertContains(response, "Žiadne úlohy")

    def test_visible_tasks(self):
        Task.objects.create(number=1, name="Test task", round=self.round)
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "Test task")

    def test_my_points_hidden(self):
        task = Task.objects.create(
            number=1,
            name="Test task",
            round=self.round,
            description_points=12,
            has_description=True,
        )
        Submit.objects.create(
            task=task,
            user=self.nonstaff_user,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            points=5,
        )

        self.client.force_login(self.nonstaff_user)
        response = self.client.get(self.url)
        self.assertContains(response, "popis:&nbsp;??")

    def test_my_points_visible(self):
        task = Task.objects.create(
            number=1,
            name="Test task",
            round=self.round,
            description_points=12,
            description_points_visible=True,
            has_description=True,
        )
        Submit.objects.create(
            task=task,
            user=self.nonstaff_user,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            points=5,
        )

        self.client.force_login(self.nonstaff_user)
        response = self.client.get(self.url)
        self.assertContains(response, "popis:&nbsp;5")


@override_settings(
    TASK_STATEMENTS_STORAGE=FileSystemStorage(
        location=path.join(path.dirname(__file__), "test_data", "statements")
    ),
    TASK_STATEMENTS_TASKS_DIR="tasks",
    TASK_STATEMENTS_PREFIX_TASK="",
    TASK_STATEMENTS_SOLUTIONS_DIR="solutions",
    TASK_STATEMENTS_HTML_DIR="html",
)
class TaskAndSolutionStatementsTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name="staff")
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(
            number=1, name="Test semester", competition=competition, year=1
        )
        self.round = Round.objects.create(
            number=1, semester=semester, visible=True, solutions_visible=True
        )
        self.invisible_round = Round.objects.create(
            number=1, semester=semester, visible=False, solutions_visible=False
        )
        self.task = Task.objects.create(number=1, name="Test task", round=self.round)
        self.staff_user = User.objects.create(username="staff")
        self.staff_user.groups.add(group)
        self.nonstaff_user = User.objects.create(username="nonstaff")
        self.task_url = reverse("task_statement", kwargs={"task_id": self.task.id})
        self.solution_url = reverse("solution_statement", kwargs={"task_id": self.task.id})
        self.point_deduction_message = (
            "You have submitted a text answer but "
            "have not submitted a description. This may lead to point deduction."
        )

    def test_invalid_task(self):
        url = reverse("task_statement", kwargs={"task_id": get_noexisting_id(Task)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        url = reverse("solution_statement", kwargs={"task_id": get_noexisting_id(Task)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invisible_round(self):
        task = Task.objects.create(number=1, name="Test task", round=self.invisible_round)
        url = reverse("task_statement", kwargs={"task_id": task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        url = reverse("solution_statement", kwargs={"task_id": task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_nonstaff_invisible_round(self):
        self.client.force_login(self.nonstaff_user)
        task = Task.objects.create(number=1, name="Test task", round=self.invisible_round)
        url = reverse("task_statement", kwargs={"task_id": task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        url = reverse("solution_statement", kwargs={"task_id": task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_invisible_round(self):
        self.client.force_login(self.staff_user)
        task = Task.objects.create(number=1, name="Test task", round=self.invisible_round)
        url = reverse("task_statement", kwargs={"task_id": task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse("solution_statement", kwargs={"task_id": task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_statement(self):
        response = self.client.get(self.task_url)
        self.assertContains(response, "Test task")
        self.assertContains(response, "test <b>html</b> task statement")
        self.assertIsInstance(response.context["task_text"], str)
        response = self.client.get(self.solution_url)
        self.assertContains(response, "Test task")
        self.assertContains(response, "test <b>html</b> solution statement")
        self.assertContains(response, "test <b>html</b> task statement")
        self.assertIsInstance(response.context["solution_text"], str)
        self.assertIsInstance(response.context["task_text"], str)

    def test_statement_logged_in(self):
        self.client.force_login(self.nonstaff_user)
        response = self.client.get(self.task_url)
        self.assertContains(response, "Test task")
        self.assertContains(response, "test <b>html</b> task statement")
        response = self.client.get(self.solution_url)
        self.assertContains(response, "Test task")
        self.assertContains(response, "test <b>html</b> solution statement")
        self.assertContains(response, "test <b>html</b> task statement")

    def test_missing_task_statement_file(self):
        task = Task.objects.create(number=3, name="Test task 3", round=self.round)
        url = reverse("task_statement", kwargs={"task_id": task.id})
        response = self.client.get(url)
        self.assertContains(response, "Test task 3")
        url = reverse("solution_statement", kwargs={"task_id": task.id})
        response = self.client.get(url)
        self.assertContains(response, "Test task 3")
        self.assertContains(response, "test <b>html</b> solution statement")

    def test_missing_solution_statement_file(self):
        task = Task.objects.create(number=2, name="Test task 2", round=self.round)
        url = reverse("solution_statement", kwargs={"task_id": task.id})
        response = self.client.get(url)
        self.assertContains(response, "Test task 2")
        self.assertContains(response, "test <b>html</b> task statement")

    def test_statement_only_text_submit(self):
        self.client.force_login(self.nonstaff_user)
        self.task.text_submit_solution = ["Password"]
        self.task.save()
        Submit.objects.create(
            task=self.task,
            user=self.nonstaff_user,
            submit_type=submit_constants.SUBMIT_TYPE_TEXT,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            points=5,
        )
        url = reverse("task_statement", kwargs={"task_id": self.task.id})
        response = self.client.get(url)
        self.assertNotContains(response, _(self.point_deduction_message))
        url = reverse("task_list", kwargs={"round_id": self.round.id})
        response = self.client.get(url)
        self.assertNotContains(response, _(self.point_deduction_message))

    def test_text_submit_zero_points(self):
        self.client.force_login(self.nonstaff_user)
        self.task.text_submit_solution = ["Password"]
        self.task.has_description = True
        self.task.save()
        Submit.objects.create(
            task=self.task,
            user=self.nonstaff_user,
            submit_type=submit_constants.SUBMIT_TYPE_TEXT,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            points=0,
        )
        url = reverse("task_statement", kwargs={"task_id": self.task.id})
        response = self.client.get(url)
        self.assertNotContains(response, _(self.point_deduction_message))
        url = reverse("task_list", kwargs={"round_id": self.round.id})
        response = self.client.get(url)
        self.assertNotContains(response, _(self.point_deduction_message))

    def test_missing_description(self):
        self.client.force_login(self.nonstaff_user)
        self.task.text_submit_solution = ["Password"]
        self.task.has_description = True
        self.task.save()
        Submit.objects.create(
            task=self.task,
            user=self.nonstaff_user,
            submit_type=submit_constants.SUBMIT_TYPE_TEXT,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            points=4,
        )
        url = reverse("task_statement", kwargs={"task_id": self.task.id})
        response = self.client.get(url)
        self.assertContains(response, _(self.point_deduction_message))
        url = reverse("task_list", kwargs={"round_id": self.round.id})
        response = self.client.get(url)
        self.assertContains(response, _(self.point_deduction_message))

    def test_missing_description_after_round_end(self):
        self.client.force_login(self.nonstaff_user)
        self.task.text_submit_solution = ["Password"]
        self.task.has_description = True
        self.task.save()
        self.round.end_time = timezone.now() + timezone.timedelta(-8)
        self.round.save()
        Submit.objects.create(
            task=self.task,
            user=self.nonstaff_user,
            submit_type=submit_constants.SUBMIT_TYPE_TEXT,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            points=4,
        )
        url = reverse("task_statement", kwargs={"task_id": self.task.id})
        response = self.client.get(url)
        self.assertNotContains(response, _(self.point_deduction_message))
        url = reverse("task_list", kwargs={"round_id": self.round.id})
        response = self.client.get(url)
        self.assertNotContains(response, _(self.point_deduction_message))

    def test_text_and_description_submitted(self):
        self.client.force_login(self.nonstaff_user)
        self.task.text_submit_solution = ["Password"]
        self.task.has_description = True
        self.task.save()
        Submit.objects.create(
            task=self.task,
            user=self.nonstaff_user,
            submit_type=submit_constants.SUBMIT_TYPE_TEXT,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            points=4,
        )
        Submit.objects.create(
            task=self.task,
            user=self.nonstaff_user,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=submit_constants.SUBMIT_STATUS_IN_QUEUE,
            points=0,
        )
        url = reverse("task_statement", kwargs={"task_id": self.task.id})
        response = self.client.get(url)
        self.assertNotContains(response, _(self.point_deduction_message))
        url = reverse("task_list", kwargs={"round_id": self.round.id})
        response = self.client.get(url)
        self.assertNotContains(response, _(self.point_deduction_message))


@override_settings(
    TASK_STATEMENTS_STORAGE=FileSystemStorage(
        location=path.join(path.dirname(__file__), "test_data", "statements")
    ),
    TASK_STATEMENTS_TASKS_DIR="tasks",
    TASK_STATEMENTS_PREFIX_TASK="",
    TASK_STATEMENTS_SOLUTIONS_DIR="solutions",
    TASK_STATEMENTS_PDF="tasks.pdf",
    TASK_STATEMENTS_SOLUTIONS_PDF="solutions.pdf",
)
class PdfDownloadTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name="staff")
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.semester = Semester.objects.create(
            number=1, name="Test semester", competition=competition, year=1
        )
        self.staff_user = User.objects.create(username="staff")
        self.staff_user.groups.add(group)
        self.nonstaff_user = User.objects.create(username="nonstaff")

    def test_invalid_task_pdf(self):
        url = reverse("view_pdf", kwargs={"round_id": get_noexisting_id(Round)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_solutions_pdf(self):
        url = reverse("view_solutions_pdf", kwargs={"round_id": get_noexisting_id(Round)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_task_pdf(self):
        round = Round.objects.create(
            number=1, semester=self.semester, visible=True, solutions_visible=True
        )
        url = reverse("view_pdf", kwargs={"round_id": round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(TASK_STATEMENTS_STORAGE=TestNonFileSystemStorage())
    def test_task_pdf_nonfilesystem_storage(self):
        round = Round.objects.create(
            number=1, semester=self.semester, visible=True, solutions_visible=True
        )
        filename = round.get_pdf_path(False)
        settings.TASK_STATEMENTS_STORAGE.add_file(filename)
        url = reverse("view_pdf", kwargs={"round_id": round.id})
        response = self.client.get(url)
        self.assertRedirects(
            response, "http://example.com/{}".format(filename), fetch_redirect_response=False
        )

    def test_solution_pdf(self):
        round = Round.objects.create(
            number=1, semester=self.semester, visible=True, solutions_visible=True
        )
        url = reverse("view_solutions_pdf", kwargs={"round_id": round.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_missing_task_pdf(self):
        round2 = Round.objects.create(
            number=2, semester=self.semester, visible=True, solutions_visible=True
        )
        url = reverse("view_pdf", kwargs={"round_id": round2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_missing_solutions_pdf(self):
        round2 = Round.objects.create(
            number=2, semester=self.semester, visible=True, solutions_visible=True
        )
        url = reverse("view_solutions_pdf", kwargs={"round_id": round2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invisible_task_pdf(self):
        round = Round.objects.create(
            number=1, semester=self.semester, visible=False, solutions_visible=False
        )
        url = reverse("view_pdf", kwargs={"round_id": round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invisible_solution_pdf(self):
        round = Round.objects.create(
            number=1, semester=self.semester, visible=True, solutions_visible=False
        )
        url = reverse("view_solutions_pdf", kwargs={"round_id": round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_nostaff_invisible_task_pdf(self):
        self.client.force_login(self.nonstaff_user)
        round = Round.objects.create(
            number=1, semester=self.semester, visible=False, solutions_visible=False
        )
        url = reverse("view_pdf", kwargs={"round_id": round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_nostaff_invisible_solution_pdf(self):
        self.client.force_login(self.nonstaff_user)
        round = Round.objects.create(
            number=1, semester=self.semester, visible=True, solutions_visible=False
        )
        url = reverse("view_solutions_pdf", kwargs={"round_id": round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_invisible_task_pdf(self):
        self.client.force_login(self.staff_user)
        round = Round.objects.create(
            number=1, semester=self.semester, visible=False, solutions_visible=False
        )
        url = reverse("view_pdf", kwargs={"round_id": round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_staff_invisible_solution_pdf(self):
        self.client.force_login(self.staff_user)
        round = Round.objects.create(
            number=1, semester=self.semester, visible=True, solutions_visible=False
        )
        url = reverse("view_solutions_pdf", kwargs={"round_id": round.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


@override_settings(
    TASK_STATEMENTS_STORAGE=FileSystemStorage(
        location=path.join(path.dirname(__file__), "test_data", "statements")
    ),
    TASK_STATEMENTS_TASKS_DIR="tasks",
    TASK_STATEMENTS_PREFIX_TASK="",
    TASK_STATEMENTS_PICTURES_DIR="pictures",
)
class ShowPictureTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name="staff")
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(
            number=1, name="Test semester", competition=competition, year=1
        )
        self.round = Round.objects.create(
            number=1, semester=semester, visible=True, solutions_visible=True
        )
        self.task = Task.objects.create(number=1, name="Test task", round=self.round)
        self.url = reverse(
            "show_picture",
            kwargs={"task_id": self.task.id, "type": "zadania", "picture": "picture.png"},
        )

    def test_task_image(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @override_settings(TASK_STATEMENTS_STORAGE=TestNonFileSystemStorage())
    def test_task_pdf_nonfilesystem_storage(self):
        filename = path.join(self.round.get_pictures_path(), "picture.png")
        settings.TASK_STATEMENTS_STORAGE.add_file(filename)
        response = self.client.get(self.url)
        self.assertRedirects(
            response, "http://example.com/{}".format(filename), fetch_redirect_response=False
        )


class TaskPeopleTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name="staff")
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(
            number=1, name="Test semester", competition=competition, year=1
        )
        self.round = Round.objects.create(
            number=1, semester=semester, visible=True, solutions_visible=True
        )
        self.task = Task.objects.create(number=1, name="Test task", round=self.round)
        self.reviewer1 = User.objects.create(username="reviewer1")
        self.reviewer2 = User.objects.create(username="reviewer2")
        self.proofreader = User.objects.create(username="proofreader")
        self.task.assign_person(self.reviewer1, constants.TASK_ROLE_REVIEWER)
        self.task.assign_person(self.reviewer2, constants.TASK_ROLE_REVIEWER)
        self.task.assign_person(self.proofreader, constants.TASK_ROLE_PROOFREADER)

    def test_get_assigned_people(self):
        reviewers = self.task.get_assigned_people_for_role(constants.TASK_ROLE_REVIEWER)
        solvers = self.task.get_assigned_people_for_role(constants.TASK_ROLE_SOLUTION_WRITER)
        proofreaders = self.task.get_assigned_people_for_role(constants.TASK_ROLE_PROOFREADER)
        self.assertEqual(len(reviewers), 2)
        self.assertIn(self.reviewer1, reviewers)
        self.assertIn(self.reviewer2, reviewers)
        self.assertEqual(proofreaders, [self.proofreader])
        self.assertEqual(len(solvers), 0)


class RoundManagerTests(TestCase):
    def setUp(self):
        self.competition = Competition.objects.create(name="TestCompetition")
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        other_competition = Competition.objects.create(name="OtherCompetition")
        semester = Semester.objects.create(
            number=1, name="Test semester", competition=self.competition, year=1
        )
        other_semester = Semester.objects.create(
            number=1, name="Other semester", competition=other_competition, year=1
        )
        start = timezone.now() + timezone.timedelta(-8)
        Round.objects.create(
            number=1,
            semester=semester,
            visible=True,
            solutions_visible=False,
            start_time=start,
            end_time=timezone.now() + timezone.timedelta(-2),
        )
        Round.objects.create(
            number=2,
            semester=semester,
            visible=True,
            solutions_visible=False,
            start_time=start,
            end_time=timezone.now() + timezone.timedelta(-1),
        )
        Round.objects.create(
            number=3,
            semester=semester,
            visible=True,
            solutions_visible=False,
            start_time=start,
            end_time=timezone.now() + timezone.timedelta(1),
        )
        Round.objects.create(
            number=2,
            semester=other_semester,
            visible=True,
            solutions_visible=False,
            start_time=start,
            end_time=timezone.now() + timezone.timedelta(-1),
        )

    def test_latest_finished_for_competition(self):
        self.assertEqual(Round.objects.latest_finished_for_competition(self.competition).number, 2)


class DashboardTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=settings.SITE_ID)
        self.url = reverse("dashboard")
        competition = Competition.objects.create(name="TestCompetition")
        competition.sites.add(self.site)
        self.semester = Semester.objects.create(
            number=1, name="Test semester 1", competition=competition, year=1
        )

    def test_dashboard_no_round(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("There is no active round currently."))

    def test_active_round(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            solutions_visible=True,
            visible=True,
            start_time=timezone.now() + timezone.timedelta(-8),
            end_time=timezone.now() + timezone.timedelta(8),
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, _("There is no active round currently."))
        self.assertContains(response, round)

    def test_two_rounds(self):
        round1 = Round.objects.create(
            number=1,
            semester=self.semester,
            solutions_visible=True,
            visible=True,
            start_time=timezone.now() + timezone.timedelta(-8),
            end_time=timezone.now() + timezone.timedelta(8),
        )
        round2 = Round.objects.create(
            number=2,
            semester=self.semester,
            solutions_visible=True,
            visible=True,
            start_time=timezone.now() + timezone.timedelta(-8),
            end_time=timezone.now() + timezone.timedelta(8),
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, _("There is no active round currently."))
        self.assertContains(response, round1)
        self.assertContains(response, round2)

    def test_invisible_round(self):
        Round.objects.create(
            number=1,
            semester=self.semester,
            visible=False,
            start_time=timezone.now() + timezone.timedelta(-8),
            end_time=timezone.now() + timezone.timedelta(8),
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("There is no active round currently."))

    def test_inactive_round(self):
        start = timezone.now() + timezone.timedelta(-8)
        end = timezone.now() + timezone.timedelta(-5)

        Round.objects.create(
            number=1, semester=self.semester, visible=True, start_time=start, end_time=end
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("There is no active round currently."))

    def test_dashboard_redirect(self):
        user = User.objects.create_user("TestUser", "test@localhost", "password")
        self.client.force_login(user)
        response = self.client.get("")
        self.assertRedirects(response, self.url)

    def test_news_count(self):
        user = User.objects.create_user("TestUser", "test@localhost", "password")

        for i in range(constants.NEWS_ENTRIES_ON_DASHBOARD + 1):
            entry = NewsEntry.objects.create(
                author=user, title="Test news entry %d" % i, text="Test text"
            )
            entry.sites.add(self.site)

        response = self.client.get(self.url)

        for i in range(constants.NEWS_ENTRIES_ON_DASHBOARD + 1):
            if i == 0:
                self.assertNotContains(response, "Test news entry %d" % i)
            else:
                self.assertContains(response, "Test news entry %d" % i)


class RoundNotificationTest(TestCase):
    def setUp(self):
        grad_year = timezone.now().year + 1
        self.user = User.objects.create_user(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=grad_year,
        )
        self.competition = Competition.objects.create(name="TestCompetition")
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.end_time_new = timezone.now() + timezone.timedelta(10)
        self.semester = Semester.objects.create(
            number=1, name="Test semester", competition=self.competition, year=1
        )

    def test_update_invisible_to_invisible(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=False,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )

        round.visible = False
        round.save()

        self.assertFalse(Notification.objects.filter(channel="round_started").exists())

    def test_update_invisible_to_visible(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=False,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )

        round.visible = True
        round.save()

        self.assertTrue(Notification.objects.filter(channel="round_started").exists())

    def test_update_visible_to_visible(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=False,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )

        round.visible = True
        round.save()

        round.visible = True
        round.save()

        query = Notification.objects.filter(channel="round_started")

        self.assertTrue(query.exists())
        self.assertEqual(query.count(), 1)


class TaskNotificationTest(TestCase):
    def setUp(self):
        grad_year = timezone.now().year + 1
        self.user = User.objects.create_user(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=grad_year,
        )
        self.competition = Competition.objects.create(name="TestCompetition")
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.end_time_new = timezone.now() + timezone.timedelta(10)
        self.semester = Semester.objects.create(
            number=1, name="Test semester", competition=self.competition, year=1
        )
        self.round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        self.task = Task.objects.create(number=1, name="Test task", round=self.round)

    def test_show_points(self):
        Submit.objects.create(
            task=self.task,
            user=self.user,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            points=5,
        )
        Submit.objects.create(
            task=self.task,
            user=self.user,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            points=7,
        )

        self.assertFalse(Notification.objects.filter(channel="submit_reviewed").exists())

        self.task.description_points_visible = True
        self.task.save()

        notification = Notification.objects.filter(channel="submit_reviewed")
        self.assertTrue(notification.exists())
        self.assertEqual(notification.count(), 1)


class TaskMethodTest(TestCase):
    def setUp(self):
        self.competition = Competition.objects.create(
            name="SusiTestCompetition", pk=SUSI_COMPETITION_ID
        )
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.semester = Semester.objects.create(
            number=1, name="Test semester", competition=self.competition, year=1
        )
        self.start_time = timezone.now() + timezone.timedelta(-100)

    def test_hints_public(self):
        end_time1 = timezone.now() + timezone.timedelta(minutes=1)
        week = timezone.timedelta(days=7)
        big_hint_delay = timezone.timedelta(days=2)
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time,
            end_time=end_time1,
            second_end_time=end_time1 + week,
            susi_big_hint_time=end_time1 + big_hint_delay,
        )
        Task.objects.create(
            pk=1,
            number=1,
            name="Test task 1",
            round=round,
            description_points_visible=True,
            description_points=6,
            susi_small_hint="SMALL_HINT",
            susi_big_hint="BIG_HINT",
        )
        url = reverse("task_statement", kwargs={"task_id": 1})

        self.assertFalse(round.susi_small_hint_public)
        self.assertFalse(round.susi_big_hint_public)
        response = self.client.get(url)
        self.assertContains(response, "Bude zverejnená")

        end_time2 = timezone.now() + timezone.timedelta(minutes=-1)
        round.end_time = end_time2
        round.susi_big_hint_time = round.end_time + big_hint_delay
        round.second_end_time = round.end_time + week
        round.save()
        self.assertTrue(round.susi_small_hint_public)
        self.assertFalse(round.susi_big_hint_public)
        response = self.client.get(url)
        self.assertContains(response, "SMALL_HINT")
        self.assertContains(response, "Bude zverejnená")

        end_time3 = timezone.now() - big_hint_delay + timezone.timedelta(minutes=1)
        round.end_time = end_time3
        round.susi_big_hint_time = round.end_time + big_hint_delay
        round.second_end_time = round.end_time + week
        round.save()
        self.assertTrue(round.susi_small_hint_public)
        self.assertFalse(round.susi_big_hint_public)
        response = self.client.get(url)
        self.assertContains(response, "SMALL_HINT")
        self.assertContains(response, "Bude zverejnená")

        end_time4 = timezone.now() - big_hint_delay + timezone.timedelta(minutes=-1)
        round.end_time = end_time4
        round.susi_big_hint_time = round.end_time + big_hint_delay
        round.second_end_time = round.end_time + week
        round.save()
        self.assertTrue(round.susi_small_hint_public)
        self.assertTrue(round.susi_big_hint_public)
        response = self.client.get(url)
        self.assertContains(response, "SMALL_HINT")
        self.assertContains(response, "BIG_HINT")
