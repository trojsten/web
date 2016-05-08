# -*- coding: utf-8 -*-

import json
import os
import xml.etree.ElementTree as ET
from django.test import TestCase, override_settings

from trojsten.contests.models import Competition, Round, Series
from trojsten.people.models import User
from django.contrib.auth.models import Group


from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import format_html
from sendfile import sendfile
from unidecode import unidecode

from django.contrib.sites.models import Site

from trojsten.contests.models import Competition, Round
from trojsten.submit.forms import (DescriptionSubmitForm, SourceSubmitForm,
                                   TestableZipSubmitForm)
from trojsten.submit.helpers import (get_path, process_submit, update_submit,
                                     write_chunks_to_file)
from trojsten.submit.templatetags.submit_parts import submitclass
from trojsten.tasks.models import Submit, Task
from trojsten.utils.test_utils import get_noexisting_id

from . import constants
from .constants import VIEWABLE_EXTENSIONS

import datetime


class SubmitListTests(TestCase):

    def setUp(self):
        self.list_url = reverse('active_rounds_submit_page')
        gradyear = datetime.datetime.now().year
        self.non_staff_user = User.objects.create_user(username="jozko", first_name="Jozko",
                                                       last_name="Mrkvicka", password="pass",
                                                       graduation=gradyear)
        self.staff_user = User.objects.create_user(username="staff", first_name="Staff",
                                                   last_name="Staff", password="pass",
                                                   graduation=2010)
        self.group = Group.objects.create(name='staff')
        self.group.user_set.add(self.staff_user)
        self.staff_user.groups.add(self.group)
        self.competition = Competition.objects.create(name='TestCompetition',
                                                      organizers_group=self.group)
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = datetime.datetime.now() + datetime.timedelta(-10)
        self.end_time_old = datetime.datetime.now() + datetime.timedelta(-5)
        self.end_time_new = datetime.datetime.now() + datetime.timedelta(10)
        self.series = Series.objects.create(number=1, name='Test series',
                                            competition=self.competition,
                                            year=1)

    def test_redirect_to_login(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)

    def test_no_round(self):
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertContains(response, "Aktuálne nebeží žiadne kolo.")

    def test_non_active_round(self):
        Round.objects.create(number=1, series=self.series, visible=True,
                             solutions_visible=False, start_time=self.start_time_old,
                             end_time=self.end_time_old)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, "Aktuálne nebeží žiadne kolo.")
        self.client.force_login(self.staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertContains(response, "Aktuálne nebeží žiadne kolo.")

    def test_non_visible_round(self):
        Round.objects.create(number=1, series=self.series, visible=False,
                             solutions_visible=False, start_time=self.start_time_old,
                             end_time=self.end_time_new)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertContains(response, "Aktuálne nebeží žiadne kolo.")
        self.client.force_login(self.staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.competition.name)
        # @ToDo: translations
        self.assertContains(response, "skryté")

    def test_visible_round(self):
        Round.objects.create(number=1, series=self.series, visible=True,
                             solutions_visible=False, start_time=self.start_time_old,
                             end_time=self.end_time_new)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.competition.name)
        self.client.force_login(self.staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.competition.name)
        # @ToDo: translations
        self.assertNotContains(response, "skryté")

    def test_task_in_round(self):
        round = Round.objects.create(number=1, series=self.series, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.competition.name)
        self.assertContains(response, task.name)
        # @ToDo: translations
        self.assertContains(response, "Tento príklad momentálne nemá možnosť odovzdávania.")

    def test_task_with_source(self):
        round = Round.objects.create(number=1, series=self.series, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        Task.objects.create(number=1, name='Test task', round=round, has_source=True)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertNotContains(response, "Tento príklad momentálne nemá možnosť odovzdávania.")
        # @ToDo: translations
        self.assertContains(response, "Kód")

    def test_task_with_description(self):
        round = Round.objects.create(number=1, series=self.series, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        Task.objects.create(number=1, name='Test task', round=round, has_description=True)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertNotContains(response, "Tento príklad momentálne nemá možnosť odovzdávania.")
        # @ToDo: translations
        self.assertContains(response, "Popis")

    def test_task_with_zip(self):
        round = Round.objects.create(number=1, series=self.series, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertNotContains(response, "Tento príklad momentálne nemá možnosť odovzdávania.")
        # @ToDo: translations
        self.assertContains(response, "Zip")

    def tesk_task_with_all_submit_types(self):
        round = Round.objects.create(number=1, series=self.series, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True,
                            has_description=True, has_source=True)
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
        gradyear = datetime.datetime.now().year
        self.non_staff_user = User.objects.create_user(username="jozko", first_name="Jozko",
                                                       last_name="Mrkvicka", password="pass",
                                                       graduation=gradyear)
        self.staff_user = User.objects.create_user(username="staff", first_name="Staff",
                                                   last_name="Staff", password="pass",
                                                   graduation=2010)
        self.group = Group.objects.create(name='staff')
        self.group.user_set.add(self.staff_user)
        self.staff_user.groups.add(self.group)
        self.competition = Competition.objects.create(name='TestCompetition',
                                                      organizers_group=self.group)
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = datetime.datetime.now() + datetime.timedelta(-10)
        self.start_time_new = datetime.datetime.now() + datetime.timedelta(5)
        self.end_time_old = datetime.datetime.now() + datetime.timedelta(-5)
        self.end_time_new = datetime.datetime.now() + datetime.timedelta(10)
        self.series = Series.objects.create(number=1, name='Test series',
                                            competition=self.competition,
                                            year=1)

    def test_redirect_to_login(self):
        url = reverse('task_submit_page', kwargs={'task_id': 47})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_non_existing_task(self):
        url = reverse('task_submit_page', kwargs={'task_id': get_noexisting_id(Task)})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    #  @FIXME: Feature not implemented yet.
    # def test_non_active_round(self):
    #     round = Round.objects.create(number=1, series=self.series, visible=False,
    #                                  solutions_visible=False, start_time=self.start_time_old,
    #                                  end_time=self.end_time_new)
    #     task = Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True,
    #                                has_description=True, has_source=True)
    #     url = reverse('task_submit_page', kwargs={'task_id': task.id})
    #     self.client.force_login(self.non_staff_user)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 404)

    def test_old_round(self):
        round = Round.objects.create(number=1, series=self.series, visible=False,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_old)
        task = Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True,
                                   has_description=True, has_source=True)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Kolo už skončilo.")

    # @FIXME: Feature not implemented yet.
    # def test_future_round(self):
    #     round = Round.objects.create(number=1, series=self.series, visible=False,
    #                                  solutions_visible=False, start_time=self.start_time_new,
    #                                  end_time=self.end_time_new)
    #     task = Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True,
    #                                has_description=True, has_source=True)
    #     url = reverse('task_submit_page', kwargs={'task_id': task.id})
    #     self.client.force_login(self.non_staff_user)
    #     response = self.client.get(url)
    #     # @ToDo: translations
    #     self.assertNotContains(response, "Submit")

    def test_non_submittable_task(self):
        round = Round.objects.create(number=1, series=self.series, visible=False,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertNotContains(response, "Zip")
        # @ToDo: translations
        self.assertNotContains(response, "Popis")
        # @ToDo: translations
        self.assertNotContains(response, "Kód")

    def test_task_with_source(self):
        round = Round.objects.create(number=1, series=self.series, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round, has_source=True)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Kód")

    def test_task_with_description(self):
        round = Round.objects.create(number=1, series=self.series, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round, has_description=True)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Popis")

    def test_task_with_zip(self):
        round = Round.objects.create(number=1, series=self.series, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Zip")

    def test_task_with_all_submit_types(self):
        round = Round.objects.create(number=1, series=self.series, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True,
                                   has_description=True, has_source=True)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
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
        gradyear = datetime.datetime.now().year
        self.non_staff_user = User.objects.create_user(username="jozko", first_name="Jozko",
                                                        last_name="Mrkvicka", password="pass",
                                                        graduation=gradyear)
        self.staff_user = User.objects.create_user(username="staff", first_name="Staff",
                                                   last_name="Staff", password="pass",
                                                   graduation=2010)
        self.group = Group.objects.create(name='staff')
        self.group.user_set.add(self.staff_user)
        self.staff_user.groups.add(self.group)
        competition = Competition.objects.create(name='TestCompetition',
                                                      organizers_group=self.group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = datetime.datetime.now() + datetime.timedelta(-10)
        self.start_time_new = datetime.datetime.now() + datetime.timedelta(5)
        self.end_time_old = datetime.datetime.now() + datetime.timedelta(-5)
        self.end_time_new = datetime.datetime.now() + datetime.timedelta(10)
        series = Series.objects.create(number=1, name='Test series',
                                            competition=competition,
                                            year=1)
        round = Round.objects.create(number=1, series=series, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        self.task = Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True)
        self.submit = Submit.objects.create(task=self.task, user=self.non_staff_user, submit_type=0, points=0)


    def test_no_access(self):
        gradyear = datetime.datetime.now().year
        url = reverse('poll_submit_info', kwargs={'submit_id': self.submit.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        non_staff_user2 = User.objects.create_user(username="jurko", first_name="Jozko",
                                                        last_name="Mrkvicka", password="pass",
                                                        graduation=gradyear)
        self.client.force_login(non_staff_user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


    def test_non_existing_submit(self):
        url = reverse('poll_submit_info', kwargs={'submit_id': get_noexisting_id(Submit)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_access_for_staff(self):
        url = reverse('poll_submit_info', kwargs={'submit_id': self.submit.id})
        self.client.force_login(self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_access_for_staff(self):
        url = reverse('poll_submit_info', kwargs={'submit_id': self.submit.id})
        self.client.force_login(self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
