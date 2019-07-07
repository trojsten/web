# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import shutil
import tempfile
import unittest
from os import path

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core import mail
from django.core.files import File
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from judge_client import constants as judge_constants

from trojsten.contests.constants import TASK_ROLE_REVIEWER
from trojsten.contests.models import Competition, Round, Semester, Task, TaskPeople
from trojsten.people.models import User
from trojsten.submit import constants
from trojsten.submit.forms import SubmitAdminForm
from trojsten.submit.helpers import (
    _get_lang_from_filename,
    get_description_file_path,
    get_path,
    write_chunks_to_file,
)
from trojsten.submit.views import send_notification_email
from trojsten.utils.test_utils import get_noexisting_id

from .models import ExternalSubmitToken, Submit


class SubmitListTests(TestCase):
    def setUp(self):
        self.list_url = reverse("active_rounds_submit_page")
        grad_year = timezone.now().year + 1
        self.non_staff_user = User.objects.create_user(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=grad_year,
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            first_name="Staff",
            last_name="Staff",
            password="pass",
            graduation=2010,
        )
        self.group = Group.objects.create(name="staff")
        self.group.user_set.add(self.staff_user)
        self.staff_user.groups.add(self.group)
        self.competition = Competition.objects.create(
            name="TestCompetition", organizers_group=self.group
        )
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.end_time_old = timezone.now() + timezone.timedelta(-5)
        self.end_time_new = timezone.now() + timezone.timedelta(10)
        self.semester = Semester.objects.create(
            number=1, name="Test semester", competition=self.competition, year=1
        )

    def test_redirect_to_login(self):
        response = self.client.get(self.list_url)
        redirect_to = "%s?next=%s" % (settings.LOGIN_URL, reverse("active_rounds_submit_page"))
        self.assertRedirects(response, redirect_to)

    def test_no_round(self):
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertContains(response, "Aktuálne nebeží žiadne kolo.")

    def test_non_active_round(self):
        Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_old,
        )
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertContains(response, "Aktuálne nebeží žiadne kolo.")
        self.client.force_login(self.staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertContains(response, "Aktuálne nebeží žiadne kolo.")

    def test_non_visible_round(self):
        Round.objects.create(
            number=1,
            semester=self.semester,
            visible=False,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertContains(response, "Aktuálne nebeží žiadne kolo.")
        self.client.force_login(self.staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.competition.name)
        # @ToDo: translations
        self.assertContains(response, "skryté")

    def test_task_without_submit(self):
        Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.competition.name)
        self.client.force_login(self.staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.competition.name)
        # @ToDo: translations
        self.assertNotContains(response, "skryté")

    def test_task_in_round(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        task = Task.objects.create(number=1, name="Test task", round=round)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.competition.name)
        self.assertContains(response, task.name)
        # @ToDo: translations
        self.assertContains(response, "Tento príklad momentálne nemá možnosť odovzdávania.")

    def test_task_with_source(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        Task.objects.create(number=1, name="Test task", round=round, has_source=True)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertNotContains(response, "Tento príklad momentálne nemá možnosť odovzdávania.")
        # @ToDo: translations
        self.assertContains(response, "Kód")

    def test_task_with_description(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        Task.objects.create(number=1, name="Test task", round=round, has_description=True)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertNotContains(response, "Tento príklad momentálne nemá možnosť odovzdávania.")
        # @ToDo: translations
        self.assertContains(response, "Popis")

    def test_task_with_zip(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        Task.objects.create(number=1, name="Test task", round=round, has_testablezip=True)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertNotContains(response, "Tento príklad momentálne nemá možnosť odovzdávania.")
        # @ToDo: translations
        self.assertContains(response, "Zip")

    def tesk_task_with_all_submit_types(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        Task.objects.create(
            number=1,
            name="Test task",
            round=round,
            has_testablezip=True,
            has_description=True,
            has_source=True,
        )
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertNotContains(response, "Tento príklad momentálne nemá možnosť odovzdávania.")
        # @ToDo: translations
        self.assertContains(response, "Zip")
        # @ToDo: translations
        self.assertContains(response, "Popis")
        # @ToDo: translations
        self.assertContains(response, "Kód")


class SubmitTaskTests(TestCase):
    def setUp(self):
        grad_year = timezone.now().year + 1
        self.non_staff_user = User.objects.create_user(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=grad_year,
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            first_name="Staff",
            last_name="Staff",
            password="pass",
            graduation=2010,
        )
        self.group = Group.objects.create(name="staff")
        self.group.user_set.add(self.staff_user)
        self.staff_user.groups.add(self.group)
        self.competition = Competition.objects.create(
            name="TestCompetition", organizers_group=self.group
        )
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.start_time_new = timezone.now() + timezone.timedelta(5)
        self.end_time_old = timezone.now() + timezone.timedelta(-5)
        self.end_time_new = timezone.now() + timezone.timedelta(10)
        self.semester = Semester.objects.create(
            number=1, name="Test semester", competition=self.competition, year=1
        )

    def test_redirect_to_login(self):
        url = reverse("task_submit_page", kwargs={"task_id": 47})
        redirect_to = "%s?next=%s" % (
            settings.LOGIN_URL,
            reverse("task_submit_page", kwargs={"task_id": 47}),
        )
        response = self.client.get(url)
        self.assertRedirects(response, redirect_to)

    def test_non_existing_task(self):
        url = reverse("task_submit_page", kwargs={"task_id": get_noexisting_id(Task)})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # @FIXME: Feature not implemented yet.
    @unittest.expectedFailure
    def test_non_active_round(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=False,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        task = Task.objects.create(
            number=1,
            name="Test task",
            round=round,
            has_testablezip=True,
            has_description=True,
            has_source=True,
        )
        url = reverse("task_submit_page", kwargs={"task_id": task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_old_round(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=False,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_old,
        )
        task = Task.objects.create(
            number=1,
            name="Test task",
            round=round,
            has_testablezip=True,
            has_description=True,
            has_source=True,
        )
        url = reverse("task_submit_page", kwargs={"task_id": task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Kolo už skončilo.")

    # @FIXME: Feature not implemented yet.
    @unittest.expectedFailure
    def test_future_round(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=False,
            solutions_visible=False,
            start_time=self.start_time_new,
            end_time=self.end_time_new,
        )
        task = Task.objects.create(
            number=1,
            name="Test task",
            round=round,
            has_testablezip=True,
            has_description=True,
            has_source=True,
        )
        url = reverse("task_submit_page", kwargs={"task_id": task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertNotContains(response, "Submit")

    def test_non_submittable_task(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=False,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        task = Task.objects.create(number=1, name="Test task", round=round)
        url = reverse("task_submit_page", kwargs={"task_id": task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertNotContains(response, "Zip")
        # @ToDo: translations
        self.assertNotContains(response, "Popis")
        # @ToDo: translations
        self.assertNotContains(response, "Kód")

    def test_task_with_source(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        task = Task.objects.create(number=1, name="Test task", round=round, has_source=True)
        url = reverse("task_submit_page", kwargs={"task_id": task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Kód")

    def test_task_with_description(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        task = Task.objects.create(number=1, name="Test task", round=round, has_description=True)
        url = reverse("task_submit_page", kwargs={"task_id": task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Popis")

    def test_task_with_zip(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        task = Task.objects.create(number=1, name="Test task", round=round, has_testablezip=True)
        url = reverse("task_submit_page", kwargs={"task_id": task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Zip")

    def test_task_with_all_submit_types(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        task = Task.objects.create(
            number=1,
            name="Test task",
            round=round,
            has_testablezip=True,
            has_description=True,
            has_source=True,
        )
        url = reverse("task_submit_page", kwargs={"task_id": task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Zip")
        # @ToDo: translations
        self.assertContains(response, "Popis")
        # @ToDo: translations
        self.assertContains(response, "Kód")


class JsonSubmitTest(TestCase):
    def setUp(self):
        self.grad_year = timezone.now().year + 1
        self.non_staff_user = User.objects.create_user(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=self.grad_year,
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            first_name="Staff",
            last_name="Staff",
            password="pass",
            graduation=2010,
        )
        self.group = Group.objects.create(name="staff")
        self.group.user_set.add(self.staff_user)
        self.staff_user.groups.add(self.group)
        competition = Competition.objects.create(
            name="TestCompetition", organizers_group=self.group
        )
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.start_time_new = timezone.now() + timezone.timedelta(5)
        self.end_time_old = timezone.now() + timezone.timedelta(-5)
        self.end_time_new = timezone.now() + timezone.timedelta(10)
        semester = Semester.objects.create(
            number=1, name="Test semester", competition=competition, year=1
        )
        round = Round.objects.create(
            number=1,
            semester=semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        self.task = Task.objects.create(
            number=1, name="Test task", round=round, has_testablezip=True
        )
        self.submit = Submit.objects.create(
            task=self.task, user=self.non_staff_user, submit_type=0, points=0
        )

    def test_no_access(self):
        url = reverse("poll_submit_info", kwargs={"submit_id": self.submit.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        non_staff_user2 = User.objects.create_user(
            username="jurko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=self.grad_year,
        )
        self.client.force_login(non_staff_user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_non_existing_submit(self):
        url = reverse("poll_submit_info", kwargs={"submit_id": get_noexisting_id(Submit)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_access_for_staff(self):
        url = reverse("poll_submit_info", kwargs={"submit_id": self.submit.id})
        self.client.force_login(self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_access_for_user(self):
        url = reverse("poll_submit_info", kwargs={"submit_id": self.submit.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        self.submit.tester_response = "ľščťžýáíéú"
        self.submit.save()
        url = reverse("poll_submit_info", kwargs={"submit_id": self.submit.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        json_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.submit.tester_response, json_response["response_verbose"])

    def test_wa_response(self):
        self.submit.tester_response = "WA"
        self.submit.save()
        url = reverse("poll_submit_info", kwargs={"submit_id": self.submit.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        json_response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(_("Wrong answer"), json_response["response_verbose"])


class JsonProtokolTest(TestCase):
    def setUp(self):
        grad_year = timezone.now().year + 1
        self.non_staff_user = User.objects.create_user(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=grad_year,
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            first_name="Staff",
            last_name="Staff",
            password="pass",
            graduation=2010,
        )
        self.group = Group.objects.create(name="staff")
        self.group.user_set.add(self.staff_user)
        self.staff_user.groups.add(self.group)
        competition = Competition.objects.create(
            name="TestCompetition", organizers_group=self.group
        )
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.start_time_new = timezone.now() + timezone.timedelta(5)
        self.end_time_old = timezone.now() + timezone.timedelta(-5)
        self.end_time_new = timezone.now() + timezone.timedelta(10)
        semester = Semester.objects.create(
            number=1, name="Test semester", competition=competition, year=1
        )
        round = Round.objects.create(
            number=1,
            semester=semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )
        self.task = Task.objects.create(
            number=1, name="Test task", round=round, has_testablezip=True
        )
        self.submit = Submit.objects.create(
            task=self.task, user=self.non_staff_user, submit_type=0, points=0
        )

    def test_no_access(self):
        grad_year = timezone.now().year + 1
        url = reverse("view_protocol", kwargs={"submit_id": self.submit.id})
        response = self.client.get(url)
        redirect_to = "%s?next=%s" % (
            settings.LOGIN_URL,
            reverse("view_protocol", kwargs={"submit_id": self.submit.id}),
        )
        self.assertRedirects(response, redirect_to)
        non_staff_user2 = User.objects.create_user(
            username="jurko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=grad_year,
        )
        self.client.force_login(non_staff_user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_non_existing_submit(self):
        self.client.force_login(self.non_staff_user)
        url = reverse("view_protocol", kwargs={"submit_id": get_noexisting_id(Submit)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_access_for_staff(self):
        url = reverse("view_protocol", kwargs={"submit_id": self.submit.id})
        self.client.force_login(self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_access_for_user(self):
        url = reverse("view_protocol", kwargs={"submit_id": self.submit.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class SubmitHelpersTests(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        self.user = User.objects.create_user(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=timezone.now().year + 1,
        )
        self.tester_user = User.objects.create(username="testovac")
        submit_ct = ContentType.objects.get(app_label="old_submit", model="submit")
        change_submit_perm = Permission.objects.get(
            content_type=submit_ct, codename="change_submit"
        )
        self.tester_user.user_permissions.add(change_submit_perm)
        self.tester_user.save()

        competition = Competition.objects.create(name="TestCompetition")
        semester = Semester.objects.create(
            number=1, name="Test semester", competition=competition, year=1
        )
        round = Round.objects.create(
            number=1, semester=semester, start_time=timezone.now(), end_time=timezone.now()
        )
        self.task = Task.objects.create(
            number=1, name="Test task", round=round, has_source=True, source_points=20
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_write_chunks_to_file(self):
        # Tests that the directory will be created
        temp_file_path = os.path.join(self.temp_dir, "dir_to_create", "tempfile")
        # Tests that we can write both bytes and unicode objects
        # (unicode will be saved with utf-8 encoding)
        write_chunks_to_file(temp_file_path, ["hello", b"world"])
        with open(temp_file_path, "rb") as f:
            data = f.read()
            self.assertEqual(data, b"helloworld")

    def test_get_lang_from_filename(self):
        self.assertEqual(_get_lang_from_filename("file.cpp"), ".cc")
        self.assertEqual(_get_lang_from_filename("file.foo"), None)

    def test_get_path(self):
        contest = self.task.round.semester.competition.name
        tester_user_id = "%s-%s" % (contest, self.user.id)
        tester_task_id = "%s-%s" % (contest, self.task.id)
        self.assertEqual(
            get_path(self.task, self.user),
            os.path.join(settings.SUBMIT_PATH, "submits", tester_user_id, tester_task_id),
        )

    def test_update_submit_ok(self):
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            submit_type=constants.SUBMIT_TYPE_SOURCE,
            points=0,
            testing_status=constants.SUBMIT_STATUS_IN_QUEUE,
            protocol_id="test_id_47",
        )
        protocol = """<protokol><runLog>
        <test><name>0.sample.a.in</name><resultCode>1</resultCode><resultMsg>OK</resultMsg><time>28</time></test>
        <test><name>0.sample.b.in</name><resultCode>1</resultCode><resultMsg>OK</resultMsg><time>28</time></test>
        <score>100</score><details>
        Score: 100
        </details><finalResult>1</finalResult><finalMessage>OK (OK: 100 %)</finalMessage></runLog></protokol>
        """
        self.client.force_login(self.tester_user)

        response = self.client.post(
            reverse("upload_protocol"), data=dict(submit_id=submit.protocol_id, protocol=protocol)
        )
        submit = Submit.objects.get(pk=submit.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(submit.testing_status, constants.SUBMIT_STATUS_FINISHED)
        self.assertEqual(submit.tester_response, judge_constants.SUBMIT_RESPONSE_OK)
        self.assertEqual(submit.points, 20)
        self.assertEqual(submit.protocol, protocol)

    def test_update_submit_corrupted_protocol(self):
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            submit_type=constants.SUBMIT_TYPE_SOURCE,
            points=0,
            testing_status=constants.SUBMIT_STATUS_IN_QUEUE,
            protocol_id="test_id_42",
        )
        protocol = """<protokol<runLog>
        <test><name>0.sample.a.in</name><resultCode>1</resultCode><resultMsg>OK</resultMsg><time>28</time></test>
        <test><name>0.sample.b.in</name><resultCode>1</resultCode><resultMsg>OK</resultMsg><time>28</time></test>
        <score>100</score><details>
        Score: 100
        </details><finalResult>1</finalResult><finalMessage>OK (OK: 100 %)</finalMessage>
        </runLog></protokol>"""
        self.client.force_login(self.tester_user)

        response = self.client.post(
            reverse("upload_protocol"), data=dict(submit_id=submit.protocol_id, protocol=protocol)
        )
        submit = Submit.objects.get(pk=submit.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(submit.testing_status, constants.SUBMIT_STATUS_FINISHED)
        self.assertEqual(submit.tester_response, judge_constants.SUBMIT_RESPONSE_PROTOCOL_CORRUPTED)
        self.assertEqual(submit.points, 0)


class ExternalSubmitKeyTests(TestCase):
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
        self.semester = Semester.objects.create(
            number=1, name="Test semester", competition=self.competition, year=1
        )
        self.round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=False,
            solutions_visible=False,
            start_time=timezone.now(),
            end_time=timezone.now(),
        )
        self.task = Task.objects.create(
            number=1,
            name="Test task",
            round=self.round,
            has_testablezip=True,
            has_description=True,
            has_source=True,
        )
        self.token = ExternalSubmitToken.objects.create(
            task=self.task, name="Test external submit token"
        )

    def _post_external_submit(self, data):
        url = reverse("external_submit")
        return self.client.post(url, json.dumps(data), content_type="application/json")

    def test_external_submit_ok(self):
        self.assertEqual(self.task.submit_set.count(), 0)
        response = self._post_external_submit(
            {"token": self.token.token, "user": self.user.pk, "points": 10}
        )
        self.assertEqual(self.task.submit_set.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_external_submit_invalid_token(self):
        response = self._post_external_submit(
            {"token": "I am a Hacker", "user": self.user.pk, "points": 10}
        )
        self.assertEqual(response.status_code, 400)

    def test_external_submit_invalid_user(self):
        response = self._post_external_submit({"token": self.token.token, "user": 0, "points": 10})
        self.assertEqual(response.status_code, 400)

    def test_external_submit_missing_parameters(self):
        response = self._post_external_submit({})
        self.assertEqual(response.status_code, 400)

    def test_external_submit_invalid_method(self):
        url = reverse("external_submit")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)


@override_settings(SUBMIT_PATH=tempfile.mkdtemp(dir=path.join(path.dirname(__file__), "test_data")))
class SubmitAdminFormTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.SUBMIT_PATH)
        super(SubmitAdminFormTests, cls).tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username="TestUser",
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=timezone.now().year + 2,
        )

        group = Group.objects.create(name="Test Group")
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(
            number=1, name="Test semester 1", year=1, competition=competition
        )

        start = timezone.now() + timezone.timedelta(-8)
        self.end = timezone.now() + timezone.timedelta(-4)
        test_round = Round.objects.create(
            number=1,
            semester=semester,
            solutions_visible=True,
            start_time=start,
            end_time=self.end,
            visible=True,
        )
        self.task = Task.objects.create(number=1, name="Test task 1", round=test_round)

    def test_create_submit(self):
        submit_file_path = path.join(
            "trojsten", "reviews", "test_data", "submits", "description.txt"
        )
        file = open(submit_file_path, "r")
        file_content = file.read()
        file.close()

        submit_file = File(open(submit_file_path, "r"), "description.txt")
        data = {
            "task": self.task.pk,
            "time": timezone.now(),
            "user": self.user.pk,
            "submit_type": constants.SUBMIT_TYPE_DESCRIPTION,
            "points": 0,
            "testing_status": constants.SUBMIT_STATUS_IN_QUEUE,
        }
        form = SubmitAdminForm(data, {"submit_file": submit_file})
        print(form.errors)
        self.assertTrue(form.is_valid())
        submit = form.save()
        file_path = get_description_file_path(file, self.user, self.task)
        self.assertEqual(submit.filepath, file_path)
        uploaded_file = open(file_path, "r")
        self.assertIsNotNone(uploaded_file)
        self.assertEqual(uploaded_file.read(), file_content)

    def test_edit_submit_time(self):
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            submit_type=constants.SUBMIT_TYPE_DESCRIPTION,
            points=0,
            testing_status=constants.SUBMIT_STATUS_IN_QUEUE,
        )
        data = SubmitAdminForm(instance=submit).initial
        new_time = timezone.now() + timezone.timedelta(-1)
        data["time"] = new_time
        form = SubmitAdminForm(data)
        self.assertTrue(form.is_valid())
        edited_submit = form.save()
        self.assertEqual(edited_submit.time, new_time)


class AllSubmitsListTest(TestCase):
    def setUp(self):
        self.url = reverse("all_submits_description_page")
        self.grad_year = timezone.now().year + 1
        self.non_staff_user = User.objects.create_user(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=self.grad_year,
        )
        self.group = Group.objects.create(name="staff")
        competition = Competition.objects.create(
            name="TestCompetition", organizers_group=self.group
        )
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time = timezone.now() + timezone.timedelta(-10)
        self.end_time = timezone.now() + timezone.timedelta(10)
        semester = Semester.objects.create(
            number=1, name="Test semester", competition=competition, year=1
        )
        round = Round.objects.create(
            number=1,
            semester=semester,
            visible=True,
            solutions_visible=False,
            start_time=self.start_time,
            end_time=self.end_time,
        )
        self.task = Task.objects.create(
            number=1, name="Test task", round=round, has_testablezip=True
        )

    def test_redirect_to_login(self):
        response = self.client.get(self.url)
        redirect_to = "%s?next=%s" % (settings.LOGIN_URL, reverse("all_submits_description_page"))
        self.assertRedirects(response, redirect_to)

    def test_in_queue_submit(self):
        self.client.force_login(self.non_staff_user)
        Submit.objects.create(
            task=self.task,
            user=self.non_staff_user,
            submit_type=constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=constants.SUBMIT_STATUS_IN_QUEUE,
            points=0,
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Test task")
        self.assertContains(response, "Neopravené")

    def test_reviewed_submit(self):
        self.client.force_login(self.non_staff_user)
        Submit.objects.create(
            task=self.task,
            user=self.non_staff_user,
            submit_type=constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=constants.SUBMIT_STATUS_REVIEWED,
            points=4,
        )
        Submit.objects.create(
            task=self.task,
            user=self.non_staff_user,
            submit_type=constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=constants.SUBMIT_STATUS_REVIEWED,
            points=7,
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Test task")
        self.assertContains(response, "Opravené")
        self.assertContains(response, "7,00")

    def test_reviewed_submit(self):
        self.client.force_login(self.non_staff_user)
        Submit.objects.create(
            task=self.task,
            user=self.non_staff_user,
            submit_type=constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=constants.SUBMIT_STATUS_IN_QUEUE,
            points=0,
        )
        Submit.objects.create(
            task=self.task,
            user=self.non_staff_user,
            submit_type=constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=constants.SUBMIT_STATUS_REVIEWED,
            points=7,
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Test task")
        self.assertContains(response, "Opravené")
        self.assertContains(response, "7,00")


class TestSubmitNotificationEmails(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="TestUser",
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=timezone.now().year + 2,
        )

        self.reviewer_1 = User.objects.create_user(
            username="staff1",
            first_name="Staff1",
            last_name="Staff1",
            password="pass",
            graduation=2010,
            email="mail1@foo.bar",
        )

        self.reviewer_2 = User.objects.create_user(
            username="staff2",
            first_name="Staff2",
            last_name="Staff2",
            password="pass",
            graduation=2010,
            email="mail2@foo.bar",
        )

        group = Group.objects.create(name="Test Group")
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(
            number=1, name="Test semester 1", year=1, competition=competition
        )

        start = timezone.now() + timezone.timedelta(-8)
        self.end = timezone.now() + timezone.timedelta(-4)
        test_round = Round.objects.create(
            number=1,
            semester=semester,
            solutions_visible=True,
            start_time=start,
            end_time=self.end,
            visible=True,
        )
        self.task = Task.objects.create(number=1, name="Test task 1", round=test_round, pk=1)

        self.task_reviewer_1 = TaskPeople.objects.create(
            role=TASK_ROLE_REVIEWER, task=self.task, user=self.reviewer_1
        )

        self.task_reviewer_2 = TaskPeople.objects.create(
            role=TASK_ROLE_REVIEWER, task=self.task, user=self.reviewer_2
        )

        self.code_submit = Submit.objects.create(
            task=self.task, user=self.user, submit_type=0, points=0, pk=1
        )
        self.desc_submit = Submit.objects.create(
            task=self.task, user=self.user, submit_type=1, points=0, pk=2
        )

    def test_send_notification_email(self):
        send_notification_email(self.code_submit, self.task.id, 0)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(email.recipients(), [self.reviewer_1.email, self.reviewer_2.email])
        self.assertIn("Jozko Mrkvicka", email.body)
        self.assertIn("example.com/admin/old_submit/submit/1/change/", email.body)
        self.assertEqual(email.from_email, "no-reply@trojsten.sk")

        mail.outbox = []

        send_notification_email(self.desc_submit, self.task.id, 1)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(email.recipients(), [self.reviewer_1.email, self.reviewer_2.email])
        self.assertIn("Jozko Mrkvicka", email.body)
        self.assertIn("example.com/admin/old_submit/submit/2/change/", email.body)
        self.assertIn("example.com/admin/contests/task/1/review/edit/2/", email.body)
        self.assertEqual(email.from_email, "no-reply@trojsten.sk")


class SubmitDetailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="TestUser",
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=timezone.now().year + 2,
        )
        self.client.force_login(self.user)
        group = Group.objects.create(name="Test Group")
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(
            number=1, name="Test semester 1", year=1, competition=competition
        )

        start = timezone.now() + timezone.timedelta(-8)
        self.end = timezone.now() + timezone.timedelta(-4)
        test_round = Round.objects.create(
            number=1,
            semester=semester,
            solutions_visible=True,
            start_time=start,
            end_time=self.end,
            visible=True,
        )
        self.task = Task.objects.create(number=1, name="Test task 1", round=test_round, pk=1)

    def test_submit_details(self):
        protocol = """<protokol><runLog>
        <test><name>0.sample.a.in</name><resultCode>1</resultCode><resultMsg>OK</resultMsg><time>28</time></test>
        <test><name>0.sample.b.in</name><resultCode>1</resultCode><resultMsg>OK</resultMsg><time>28</time></test>
        <score>100</score><details>
        Score: 100
        </details><finalResult>1</finalResult><finalMessage>OK (OK: 100 %)</finalMessage></runLog></protokol>
        """
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            submit_type=constants.SUBMIT_TYPE_SOURCE,
            points=20,
            testing_status=constants.SUBMIT_STATUS_FINISHED,
            tester_response="OK",
            protocol_id="test_id_47",
            protocol=protocol,
        )
        submit = Submit.objects.get(pk=submit.pk)

        url = reverse("view_submit", kwargs={"submit_id": submit.pk})
        response = self.client.get(url)

        self.assertContains(response, "0.sample.a.in")
        self.assertContains(response, "OK")
