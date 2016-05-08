#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
try:
    from urllib import quote, unquote
except:
    from urllib.request import quote, unquote

import datetime
try:
    from urllib.request import quote
except ImportError:
    from urllib import quote

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.text import slugify

from trojsten.contests.models import Competition, Round, Series
from trojsten.tasks.models import Submit
from trojsten.tasks.models import Task
from trojsten.reviews.forms import ZipForm
from trojsten.people.models import User
from trojsten.utils.test_utils import get_noexisting_id

from trojsten.submit.constants import SUBMIT_STATUS_REVIEWED

class ReviewZipFormTests(TestCase):
    def setUp(self):
        self.choices = [(47, 'Meno Priezvisko')]
        self.test_str = u'ľščťžýáíéúňďôä'
        self.test_str_win1250 = self.test_str.encode('cp1250')
        self.test_str_utf8 = self.test_str.encode('utf8')
        self.valid_files_win1250 = set([self.test_str_win1250])
        self.valid_files_utf8 = set([self.test_str_utf8])
        if sys.version_info[0] == 3:
            # FIXME: remove this check when we stop supporting python2.7
            self.valid_files_win1250 = set([unquote(quote(self.test_str_win1250))])
            self.valid_files_utf8 = set([self.test_str_utf8.decode('utf8')])
        self.user = User(pk=47)
        self.user.save()
        pass

    def test_win_1250_valid(self):
        d = ZipForm({
            'filename': quote(self.test_str_win1250),
            'points': 3,
            'user': 47,
            'comment': self.test_str
        }, choices=self.choices, max_value=47, valid_files=self.valid_files_win1250)
        self.assertTrue(d.is_valid())

    def test_win_1250_encode(self):
        z = ZipForm(initial={
            'filename': self.test_str_win1250,
            'points': 3,
            'user': 47,
            'comment': self.test_str_win1250,
        }, choices=self.choices, max_value=47, valid_files=self.valid_files_win1250)

        self.assertEqual(z.initial['filename'], quote(self.test_str_win1250))
        self.assertEqual(z.initial['comment'], self.test_str)

    def test_utf8_valid(self):
        d = ZipForm({
            'filename': quote(self.test_str_utf8),
            'points': 3,
            'user': 47,
            'comment': self.test_str
        }, choices=self.choices, max_value=47, valid_files=self.valid_files_utf8)
        self.assertTrue(d.is_valid())

    def test_utf8_encode(self):
        z = ZipForm(initial={
            'filename': self.test_str_utf8,
            'points': 3,
            'user': 47,
            'comment': self.test_str_utf8,
        }, choices=self.choices, max_value=47, valid_files=self.valid_files_utf8)

        self.assertEqual(z.initial['filename'], quote(self.test_str_utf8))
        self.assertEqual(z.initial['comment'], self.test_str)


class ReviewTest(TestCase):
    def setUp(self):
        year = datetime.datetime.now().year + 2
        self.user = User.objects.create_user(username="TestUser", password="password",
                                             first_name="Jozko", last_name="Mrkvicka",
                                             graduation=year)
        self.staff = User.objects.create_user(username="TestStaff", password="password",
                                              first_name="Jozko", last_name="Veduci",
                                              graduation=2014)
        self.staff.is_staff = True
        self.staff.save()

        group = Group.objects.create(name="Test Group")
        group.user_set.add(self.staff)
        competition = Competition.objects.create(name='TestCompetition', organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series 1', year=1,
                                       competition=competition)

        start = datetime.datetime.now() + datetime.timedelta(-8)
        end = datetime.datetime.now() + datetime.timedelta(-4)
        test_round = Round.objects.create(number=1, series=series, solutions_visible=True,
                                          start_time=start, end_time=end, visible=True)
        self.no_submit_task = Task.objects.create(number=1, name='Test task 1', round=test_round)
        self.task = Task.objects.create(number=2, name='Test task 2', round=test_round)
        self.submit = Submit.objects.create(task=self.task, user=self.user, submit_type=1, points=5)
        self.submit.time = self.task.round.start_time + datetime.timedelta(0, 5)
        self.submit.save()

    def tearDown(self):
        self.client.logout()

    def test_redirect_to_login(self):
        url = reverse('admin:review_task', kwargs={'task_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_invalid_task(self):
        self.client.force_login(self.staff)
        url = reverse('admin:review_task', kwargs={'task_pk': get_noexisting_id(Task)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_not_in_group(self):
        staff = User.objects.create_user(username="TestStaffOther", password="password",
                                         first_name="Jozko", last_name="Veduci",
                                         graduation=2014)
        staff.is_staff = True
        staff.save()
        self.client.force_login(staff)
        url = reverse('admin:review_task', kwargs={'task_pk': self.no_submit_task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_valid_task(self):
        self.client.force_login(self.staff)
        url = reverse('admin:review_task', kwargs={'task_pk': self.no_submit_task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.no_submit_task.name)

    def test_not_reviewable_submit(self):
        for s_type in [0, 2, 3]:
            submit = Submit.objects.create(task=self.no_submit_task, user=self.user,
                                           submit_type=s_type, points=5)
            submit.time = self.no_submit_task.round.start_time + datetime.timedelta(0, 5)
            submit.save()
        self.client.force_login(self.staff)
        url = reverse('admin:review_task', kwargs={'task_pk': self.no_submit_task.id})
        response = self.client.get(url)
        self.assertNotContains(response, self.user.get_full_name())

    def test_description_submit(self):
        self.client.force_login(self.staff)
        url = reverse('admin:review_task', kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        self.assertContains(response, self.user.get_full_name())

    def test_reviewed(self):
        comment = "TESTINGcomment"
        self.client.force_login(self.staff)
        url = reverse('admin:review_task', kwargs={'task_pk': self.task.id})

        self.submit.reviewer_comment = comment
        self.submit.save()
        response = self.client.get(url)
        self.assertNotContains(response, comment)

        self.submit.testing_status = SUBMIT_STATUS_REVIEWED
        self.submit.save()
        response = self.client.get(url)
        self.assertContains(response, comment)


class DownloadLatestSubmits(TestCase):
    def setUp(self):
        year = datetime.datetime.now().year + 2
        self.user = User.objects.create_user(username="TestUser", password="password",
                                             first_name="Jozko", last_name="Mrkvicka",
                                             graduation=year)
        self.staff = User.objects.create_user(username="TestStaff", password="password",
                                              first_name="Jozko", last_name="Veduci",
                                              graduation=2014)
        self.staff.is_staff = True
        self.staff.save()

        group = Group.objects.create(name="Test Group")
        group.user_set.add(self.staff)
        competition = Competition.objects.create(name='TestCompetition', organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series 1', year=1,
                                       competition=competition)

        test_round = Round.objects.create(number=1, series=series, solutions_visible=True,
                                          visible=True)
        self.task = Task.objects.create(number=2, name='TestTask2', round=test_round)

    def tearDown(self):
        self.client.logout()

    def test_redirect_to_login(self):
        url = reverse('admin:download_latest_submits', kwargs={'task_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_invalid_task(self):
        self.client.force_login(self.staff)
        url = reverse('admin:download_latest_submits', kwargs={'task_pk': get_noexisting_id(Task)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_not_in_group(self):
        staff = User.objects.create_user(username="TestStaffOther", password="password",
                                         first_name="Jozko", last_name="Veduci",
                                         graduation=2014)
        staff.is_staff = True
        staff.save()
        self.client.force_login(staff)
        url = reverse('admin:download_latest_submits', kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_valid_task(self):
        self.client.force_login(self.staff)
        url = reverse('admin:download_latest_submits', kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertRegexpMatches(
            response['Content-Disposition'], r'filename=.*'+slugify(self.task.name)+'.*'
        )


class ReviewEditTest(TestCase):
    def setUp(self):
        year = datetime.datetime.now().year + 2
        self.user = User.objects.create_user(username="TestUser", password="password",
                                             first_name="Jozko", last_name="Mrkvicka",
                                             graduation=year)
        self.staff = User.objects.create_user(username="TestStaff", password="password",
                                              first_name="Jozko", last_name="Veduci",
                                              graduation=2014)
        self.staff.is_staff = True
        self.staff.save()

        group = Group.objects.create(name="Test Group")
        group.user_set.add(self.staff)
        competition = Competition.objects.create(name='TestCompetition', organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series 1', year=1,
                                       competition=competition)

        start = datetime.datetime.now() + datetime.timedelta(-8)
        end = datetime.datetime.now() + datetime.timedelta(-4)
        test_round = Round.objects.create(number=1, series=series, solutions_visible=True,
                                          start_time=start, end_time=end, visible=True)
        self.task = Task.objects.create(number=2, name='Test task 2', round=test_round)
        self.submit = Submit.objects.create(task=self.task, user=self.user, submit_type=1, points=5)
        self.submit.time = self.task.round.start_time + datetime.timedelta(0, 5)
        self.submit.save()

    def tearDown(self):
        self.client.logout()

    def test_redirect_to_login(self):
        url = reverse('admin:review_edit', kwargs={'task_pk': 1, 'submit_pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_invalid_task(self):
        self.client.force_login(self.staff)
        url = reverse('admin:review_edit', kwargs={'task_pk': get_noexisting_id(Task),
                      'submit_pk': get_noexisting_id(Submit)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_not_in_group(self):
        staff = User.objects.create_user(username="TestStaffOther", password="password",
                                         first_name="Jozko", last_name="Veduci",
                                         graduation=2014)
        staff.is_staff = True
        staff.save()
        self.client.force_login(staff)
        url = reverse('admin:review_edit',
                      kwargs={'task_pk': self.task.id, 'submit_pk': self.submit.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_valid_task(self):
        self.client.force_login(self.staff)
        url = reverse('admin:review_edit',
                      kwargs={'task_pk': self.task.id, 'submit_pk': self.submit.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.name)
        self.assertContains(response, self.user.get_full_name())

    def test_reviewed(self):
        comment = "TESTINGcomment"
        self.client.force_login(self.staff)
        url = reverse('admin:review_edit',
                      kwargs={'task_pk': self.task.id, 'submit_pk': self.submit.id})

        response = self.client.get(url)
        self.assertNotContains(response, comment)

        self.submit.reviewer_comment = comment
        self.submit.save()
        response = self.client.get(url)
        self.assertContains(response, comment)
