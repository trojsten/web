# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
import unittest
import json
import os
import shutil
import socket
import tempfile
import threading
import time

from trojsten.contests.models import Competition, Round, Semester, Task
from trojsten.people.models import User
from django.contrib.auth.models import Group

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from django.contrib.sites.models import Site

from trojsten.submit.helpers import write_chunks_to_file, get_lang_from_filename, get_path_raw, post_submit
from trojsten.utils.test_utils import get_noexisting_id
from .models import Submit, ExternalSubmitToken
from django.utils import timezone


class SubmitListTests(TestCase):

    def setUp(self):
        self.list_url = reverse('active_rounds_submit_page')
        grad_year = timezone.now().year + 1
        self.non_staff_user = User.objects.create_user(username='jozko', first_name='Jozko',
                                                       last_name='Mrkvicka', password='pass',
                                                       graduation=grad_year)
        self.staff_user = User.objects.create_user(username='staff', first_name='Staff',
                                                   last_name='Staff', password='pass',
                                                   graduation=2010)
        self.group = Group.objects.create(name='staff')
        self.group.user_set.add(self.staff_user)
        self.staff_user.groups.add(self.group)
        self.competition = Competition.objects.create(name='TestCompetition',
                                                      organizers_group=self.group)
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.end_time_old = timezone.now() + timezone.timedelta(-5)
        self.end_time_new = timezone.now() + timezone.timedelta(10)
        self.semester = Semester.objects.create(
            number=1, name='Test semester', competition=self.competition, year=1)

    def test_redirect_to_login(self):
        response = self.client.get(self.list_url)
        redirect_to = '%s?next=%s' % (settings.LOGIN_URL, reverse('active_rounds_submit_page'))
        self.assertRedirects(response, redirect_to)

    def test_no_round(self):
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertContains(response, 'Aktuálne nebeží žiadne kolo.')

    def test_non_active_round(self):
        Round.objects.create(number=1, semester=self.semester, visible=True,
                             solutions_visible=False, start_time=self.start_time_old,
                             end_time=self.end_time_old)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertContains(response, 'Aktuálne nebeží žiadne kolo.')
        self.client.force_login(self.staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertContains(response, 'Aktuálne nebeží žiadne kolo.')

    def test_non_visible_round(self):
        Round.objects.create(number=1, semester=self.semester, visible=False,
                             solutions_visible=False, start_time=self.start_time_old,
                             end_time=self.end_time_new)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertContains(response, 'Aktuálne nebeží žiadne kolo.')
        self.client.force_login(self.staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.competition.name)
        # @ToDo: translations
        self.assertContains(response, 'skryté')

    def test_task_without_submit(self):
        Round.objects.create(number=1, semester=self.semester, visible=True,
                             solutions_visible=False, start_time=self.start_time_old,
                             end_time=self.end_time_new)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.competition.name)
        self.client.force_login(self.staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.competition.name)
        # @ToDo: translations
        self.assertNotContains(response, 'skryté')

    def test_task_in_round(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        self.assertContains(response, self.competition.name)
        self.assertContains(response, task.name)
        # @ToDo: translations
        self.assertContains(response, 'Tento príklad momentálne nemá možnosť odovzdávania.')

    def test_task_with_source(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        Task.objects.create(number=1, name='Test task', round=round, has_source=True)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertNotContains(response, 'Tento príklad momentálne nemá možnosť odovzdávania.')
        # @ToDo: translations
        self.assertContains(response, 'Kód')

    def test_task_with_description(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        Task.objects.create(number=1, name='Test task', round=round, has_description=True)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertNotContains(response, 'Tento príklad momentálne nemá možnosť odovzdávania.')
        # @ToDo: translations
        self.assertContains(response, 'Popis')

    def test_task_with_zip(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertNotContains(response, 'Tento príklad momentálne nemá možnosť odovzdávania.')
        # @ToDo: translations
        self.assertContains(response, 'Zip')

    def tesk_task_with_all_submit_types(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True,
                            has_description=True, has_source=True)
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.list_url)
        # @ToDo: translations
        self.assertNotContains(response, 'Tento príklad momentálne nemá možnosť odovzdávania.')
        # @ToDo: translations
        self.assertContains(response, 'Zip')
        # @ToDo: translations
        self.assertContains(response, 'Popis')
        # @ToDo: translations
        self.assertContains(response, 'Kód')


class SubmitTaskTests(TestCase):

    def setUp(self):
        grad_year = timezone.now().year + 1
        self.non_staff_user = User.objects.create_user(username='jozko', first_name='Jozko',
                                                       last_name='Mrkvicka', password='pass',
                                                       graduation=grad_year)
        self.staff_user = User.objects.create_user(username='staff', first_name='Staff',
                                                   last_name='Staff', password='pass',
                                                   graduation=2010)
        self.group = Group.objects.create(name='staff')
        self.group.user_set.add(self.staff_user)
        self.staff_user.groups.add(self.group)
        self.competition = Competition.objects.create(name='TestCompetition',
                                                      organizers_group=self.group)
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.start_time_new = timezone.now() + timezone.timedelta(5)
        self.end_time_old = timezone.now() + timezone.timedelta(-5)
        self.end_time_new = timezone.now() + timezone.timedelta(10)
        self.semester = Semester.objects.create(
            number=1, name='Test semester', competition=self.competition, year=1)

    def test_redirect_to_login(self):
        url = reverse('task_submit_page', kwargs={'task_id': 47})
        redirect_to = '%s?next=%s' % (settings.LOGIN_URL, reverse('task_submit_page',
                                                                  kwargs={'task_id': 47}))
        response = self.client.get(url)
        self.assertRedirects(response, redirect_to)

    def test_non_existing_task(self):
        url = reverse('task_submit_page', kwargs={'task_id': get_noexisting_id(Task)})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    #   @FIXME: Feature not implemented yet.
    @unittest.expectedFailure
    def test_non_active_round(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=False,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True,
                                   has_description=True, has_source=True)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_old_round(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=False,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_old)
        task = Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True,
                                   has_description=True, has_source=True)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, 'Kolo už skončilo.')

    #   @FIXME: Feature not implemented yet.
    @unittest.expectedFailure
    def test_future_round(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=False,
                                     solutions_visible=False, start_time=self.start_time_new,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True,
                                   has_description=True, has_source=True)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertNotContains(response, 'Submit')

    def test_non_submittable_task(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=False,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertNotContains(response, 'Zip')
        # @ToDo: translations
        self.assertNotContains(response, 'Popis')
        # @ToDo: translations
        self.assertNotContains(response, 'Kód')

    def test_task_with_source(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round, has_source=True)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, 'Kód')

    def test_task_with_description(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round, has_description=True)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, 'Popis')

    def test_task_with_zip(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, 'Zip')

    def test_task_with_all_submit_types(self):
        round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        task = Task.objects.create(number=1, name='Test task', round=round, has_testablezip=True,
                                   has_description=True, has_source=True)
        url = reverse('task_submit_page', kwargs={'task_id': task.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, 'Zip')
        # @ToDo: translations
        self.assertContains(response, 'Popis')
        # @ToDo: translations
        self.assertContains(response, 'Kód')


class JsonSubmitTest(TestCase):

    def setUp(self):
        self.grad_year = timezone.now().year + 1
        self.non_staff_user = User.objects.create_user(username='jozko', first_name='Jozko',
                                                       last_name='Mrkvicka', password='pass',
                                                       graduation=self.grad_year)
        self.staff_user = User.objects.create_user(username='staff', first_name='Staff',
                                                   last_name='Staff', password='pass',
                                                   graduation=2010)
        self.group = Group.objects.create(name='staff')
        self.group.user_set.add(self.staff_user)
        self.staff_user.groups.add(self.group)
        competition = Competition.objects.create(name='TestCompetition',
                                                 organizers_group=self.group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.start_time_new = timezone.now() + timezone.timedelta(5)
        self.end_time_old = timezone.now() + timezone.timedelta(-5)
        self.end_time_new = timezone.now() + timezone.timedelta(10)
        semester = Semester.objects.create(
            number=1, name='Test semester', competition=competition, year=1)
        round = Round.objects.create(number=1, semester=semester, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        self.task = Task.objects.create(number=1, name='Test task', round=round,
                                        has_testablezip=True)
        self.submit = Submit.objects.create(task=self.task, user=self.non_staff_user,
                                            submit_type=0, points=0)

    def test_no_access(self):
        url = reverse('poll_submit_info', kwargs={'submit_id': self.submit.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        non_staff_user2 = User.objects.create_user(username='jurko', first_name='Jozko',
                                                   last_name='Mrkvicka', password='pass',
                                                   graduation=self.grad_year)
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

    def test_access_for_user(self):
        url = reverse('poll_submit_info', kwargs={'submit_id': self.submit.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        self.submit.tester_response = 'ľščťžýáíéú'
        self.submit.save()
        url = reverse('poll_submit_info', kwargs={'submit_id': self.submit.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.submit.tester_response, json_response['response_verbose'])

    def test_wa_response(self):
        self.submit.tester_response = 'WA'
        self.submit.save()
        url = reverse('poll_submit_info', kwargs={'submit_id': self.submit.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(_('Wrong answer'), json_response['response_verbose'])


class JsonProtokolTest(TestCase):

    def setUp(self):
        grad_year = timezone.now().year + 1
        self.non_staff_user = User.objects.create_user(username='jozko', first_name='Jozko',
                                                       last_name='Mrkvicka', password='pass',
                                                       graduation=grad_year)
        self.staff_user = User.objects.create_user(username='staff', first_name='Staff',
                                                   last_name='Staff', password='pass',
                                                   graduation=2010)
        self.group = Group.objects.create(name='staff')
        self.group.user_set.add(self.staff_user)
        self.staff_user.groups.add(self.group)
        competition = Competition.objects.create(name='TestCompetition',
                                                 organizers_group=self.group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.start_time_new = timezone.now() + timezone.timedelta(5)
        self.end_time_old = timezone.now() + timezone.timedelta(-5)
        self.end_time_new = timezone.now() + timezone.timedelta(10)
        semester = Semester.objects.create(
            number=1, name='Test semester', competition=competition, year=1)
        round = Round.objects.create(number=1, semester=semester, visible=True,
                                     solutions_visible=False, start_time=self.start_time_old,
                                     end_time=self.end_time_new)
        self.task = Task.objects.create(number=1, name='Test task', round=round,
                                        has_testablezip=True)
        self.submit = Submit.objects.create(task=self.task, user=self.non_staff_user,
                                            submit_type=0, points=0)

    def test_no_access(self):
        grad_year = timezone.now().year + 1
        url = reverse('view_protocol', kwargs={'submit_id': self.submit.id})
        response = self.client.get(url)
        redirect_to = '%s?next=%s' % (settings.LOGIN_URL, reverse('view_protocol',
                                                                  kwargs={'submit_id': self.submit.id}))
        self.assertRedirects(response, redirect_to)
        non_staff_user2 = User.objects.create_user(username='jurko', first_name='Jozko',
                                                   last_name='Mrkvicka', password='pass',
                                                   graduation=grad_year)
        self.client.force_login(non_staff_user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_non_existing_submit(self):
        self.client.force_login(self.non_staff_user)
        url = reverse('view_protocol', kwargs={'submit_id': get_noexisting_id(Submit)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_access_for_staff(self):
        url = reverse('view_protocol', kwargs={'submit_id': self.submit.id})
        self.client.force_login(self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_access_for_user(self):
        url = reverse('view_protocol', kwargs={'submit_id': self.submit.id})
        self.client.force_login(self.non_staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class SubmitHelpersTests(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_write_chunks_to_file(self):
        # Tests that the directory will be created
        temp_file_path = os.path.join(self.temp_dir, "dir_to_create", "tempfile")
        # Tests that we can write both bytes and unicode objects (unicode will be saved with utf-8 encoding
        write_chunks_to_file(temp_file_path, [u"hello", b"world"])
        with open(temp_file_path, 'rb') as f:
            data = f.read()
            self.assertEqual(data, b"helloworld")

    def test_get_lang_from_filename(self):
        self.assertEqual(get_lang_from_filename("file.cpp"), ".cc")
        self.assertEqual(get_lang_from_filename("file.foo"), False)

    def test_get_path_raw(self):
        self.assertEqual(get_path_raw("contest", "task", "user"),
                         os.path.join(settings.SUBMIT_PATH, "submits", "user", "task"))

    def test_post_submit(self):
        def run_fake_server(test):
            server_sock = socket.socket()
            server_sock.bind(('127.0.0.1', 7777))
            server_sock.listen(0)
            conn, addr = server_sock.accept()
            raw = conn.recv(2048)
            data = conn.recv(2048)
            server_sock.close()
            test.received = raw + data

        server_thread = threading.Thread(target=run_fake_server, args=(self,))
        server_thread.start()
        time.sleep(50.0 / 1000.0)  # 50ms should be enough for the server to bind
        post_submit(u"raw", b"data")
        server_thread.join()
        self.assertEqual(self.received, b"rawdata")


class ExternalSubmitKeyTests(TestCase):

    def setUp(self):
        grad_year = timezone.now().year + 1
        self.user = User.objects.create_user(
            username='jozko', first_name='Jozko', last_name='Mrkvicka',
            password='pass', graduation=grad_year
        )
        self.competition = Competition.objects.create(
            name='TestCompetition'
        )
        self.semester = Semester.objects.create(
            number=1, name='Test semester',
            competition=self.competition, year=1
        )
        self.round = Round.objects.create(
            number=1, semester=self.semester, visible=False,
            solutions_visible=False, start_time=timezone.now(),
            end_time=timezone.now(),
        )
        self.task = Task.objects.create(
            number=1, name='Test task', round=self.round,
            has_testablezip=True, has_description=True,
            has_source=True,
        )
        self.token = ExternalSubmitToken.objects.create(
            task=self.task, name="Test external submit token"
        )

    def _post_external_submit(self, data):
        url = reverse('external_submit')
        return self.client.post(
            url, json.dumps(data),
            content_type="application/json",
        )

    def test_external_submit_ok(self):
        self.assertEqual(self.task.submit_set.count(), 0)
        response = self._post_external_submit({
            "token": self.token.token,
            "user": self.user.pk,
            "points": 10,
        })
        self.assertEqual(self.task.submit_set.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_external_submit_invalid_token(self):
        response = self._post_external_submit({
            "token": "I am a Hacker",
            "user": self.user.pk,
            "points": 10,
        })
        self.assertEqual(response.status_code, 400)

    def test_external_submit_invalid_user(self):
        response = self._post_external_submit({
            "token": self.token.token,
            "user": 0,
            "points": 10,
        })
        self.assertEqual(response.status_code, 400)

    def test_external_submit_missing_parameters(self):
        response = self._post_external_submit({})
        self.assertEqual(response.status_code, 400)

    def test_external_submit_invalid_method(self):
        url = reverse('external_submit')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
