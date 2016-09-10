#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import shutil
import sys
import tempfile
import zipfile
from os import path

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.utils import timezone
from django.utils.text import slugify

from trojsten.contests.models import Competition, Round, Series, Task
from trojsten.people.models import User
from trojsten.reviews import constants as review_constants
from trojsten.reviews import helpers
from trojsten.reviews.forms import ZipForm
from trojsten.submit import constants as submit_constants
from trojsten.submit.models import Submit
from trojsten.utils.test_utils import get_noexisting_id

try:
    from urllib.request import quote, unquote
except ImportError:
    from urllib import quote, unquote


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
        year = timezone.now().year + 2
        self.user = User.objects.create_user(username='TestUser', password='password',
                                             first_name='Jozko', last_name='Mrkvicka',
                                             graduation=year)
        self.staff = User.objects.create_user(username='TestStaff', password='password',
                                              first_name='Jozko', last_name='Veduci',
                                              graduation=2014)
        self.staff.is_staff = True
        self.staff.save()

        group = Group.objects.create(name='Test Group')
        group.user_set.add(self.staff)
        competition = Competition.objects.create(name='TestCompetition', organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series 1', year=1,
                                       competition=competition)

        start = timezone.now() + timezone.timedelta(-8)
        end = timezone.now() + timezone.timedelta(-4)
        test_round = Round.objects.create(number=1, series=series, solutions_visible=True,
                                          start_time=start, end_time=end, visible=True)
        self.no_submit_task = Task.objects.create(number=1, name='Test task 1', round=test_round)
        self.task = Task.objects.create(number=2, name='Test task 2', round=test_round)
        self.submit = Submit.objects.create(task=self.task, user=self.user, submit_type=1, points=5)
        self.submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        self.submit.save()

        self.url_name = 'admin:review_task'

    def test_redirect_to_login(self):
        # Najprv sa posle na login, potom na admin login, a az potom na povodnu stranku.
        # Posledna cast za next je double quoted, posledne next je len quoted.
        url = reverse(self.url_name, kwargs={'task_pk': 1})
        response = self.client.get(url, follow=True)
        login_url = settings.LOGIN_URL
        admin_login_url = '?next=%s' % reverse('admin:login')
        last_url = quote(url, safe='')
        last_url = quote('?next=%s' % last_url, safe='')
        redirect_to = '%s%s%s' % (login_url, admin_login_url, last_url)
        self.assertRedirects(response, redirect_to)

    def test_redirect_to_admin_login(self):
        # Tato url nie je vobec quoted.
        url = reverse(self.url_name, kwargs={'task_pk': 1})
        response = self.client.get(url, follow=True)
        self.client.force_login(self.user)
        response = self.client.get(url)
        redirect_to = '%s?next=%s' % (reverse('admin:login'), url)
        self.assertRedirects(response, redirect_to)

    def test_invalid_task(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': get_noexisting_id(Task)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_not_in_group(self):
        staff = User.objects.create_user(username='TestStaffOther', password='password',
                                         first_name='Jozko', last_name='Veduci',
                                         graduation=2014)
        staff.is_staff = True
        staff.save()
        self.client.force_login(staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.no_submit_task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_valid_task(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.no_submit_task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.no_submit_task.name)

    def test_not_reviewable_submit(self):
        for s_type in [
            submit_constants.SUBMIT_TYPE_SOURCE,
            submit_constants.SUBMIT_TYPE_TESTABLE_ZIP,
            submit_constants.SUBMIT_TYPE_EXTERNAL
        ]:
            submit = Submit.objects.create(task=self.no_submit_task, user=self.user,
                                           submit_type=s_type, points=5)
            submit.time = self.no_submit_task.round.start_time + timezone.timedelta(0, 5)
            submit.save()
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.no_submit_task.id})
        response = self.client.get(url)
        self.assertNotContains(response, self.user.get_full_name())

    def test_description_submit(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        self.assertContains(response, self.user.get_full_name())

    def test_reviewed(self):
        comment = 'TESTINGcomment'
        multi_line_comment = '''Comment
        On
        More
        Lines'''
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.task.id})

        self.submit.reviewer_comment = comment
        self.submit.save()
        response = self.client.get(url)
        self.assertNotContains(response, comment)
        self.assertNotContains(response, multi_line_comment)

        self.submit.testing_status = submit_constants.SUBMIT_STATUS_REVIEWED
        self.submit.save()
        response = self.client.get(url)
        self.assertContains(response, comment)

        self.submit.reviewer_comment = multi_line_comment
        self.submit.save()
        response = self.client.get(url)
        self.assertNotContains(response, comment)
        self.assertContains(response, multi_line_comment)


@override_settings(
    SUBMIT_PATH=tempfile.mkdtemp(dir=path.join(path.dirname(__file__), 'test_data')),
)
class DownloadLatestSubmits(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.SUBMIT_PATH)
        super(DownloadLatestSubmits, cls).tearDownClass()

    def setUp(self):
        year = timezone.now().year + 2
        self.user = User.objects.create_user(username='TestUser', password='password',
                                             first_name='Jozko', last_name='Mrkvicka',
                                             graduation=year)
        self.staff = User.objects.create_user(username='TestStaff', password='password',
                                              first_name='Jozko', last_name='Veduci',
                                              graduation=2014)
        self.staff.is_staff = True
        self.staff.save()

        group = Group.objects.create(name='Test Group')
        group.user_set.add(self.staff)
        competition = Competition.objects.create(name='TestCompetition', organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series 1', year=1,
                                       competition=competition)

        test_round = Round.objects.create(number=1, series=series, solutions_visible=True,
                                          visible=True)
        self.task = Task.objects.create(number=2, name='TestTask2', round=test_round)

        self.url_name = 'admin:download_latest_submits'

    def test_redirect_to_login(self):
        # Najprv sa posle na login, potom na admin login, a az potom na povodnu stranku.
        # Posledna cast za next je double quoted, posledne next je len quoted.
        url = reverse(self.url_name, kwargs={'task_pk': 1})
        response = self.client.get(url, follow=True)
        login_url = settings.LOGIN_URL
        admin_login_url = '?next=%s' % reverse('admin:login')
        last_url = quote(url, safe='')
        last_url = quote('?next=%s' % last_url, safe='')
        redirect_to = '%s%s%s' % (login_url, admin_login_url, last_url)
        self.assertRedirects(response, redirect_to)

    def test_redirect_to_admin_login(self):
        # Tato url nie je vobec quoted.
        url = reverse(self.url_name, kwargs={'task_pk': 1})
        response = self.client.get(url, follow=True)
        self.client.force_login(self.user)
        response = self.client.get(url)
        redirect_to = '%s?next=%s' % (reverse('admin:login'), url)
        self.assertRedirects(response, redirect_to)

    def test_invalid_task(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': get_noexisting_id(Task)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_not_in_group(self):
        staff = User.objects.create_user(username='TestStaffOther', password='password',
                                         first_name='Jozko', last_name='Veduci',
                                         graduation=2014)
        staff.is_staff = True
        staff.save()
        self.client.force_login(staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_valid_task(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertRegexpMatches(
            response['Content-Disposition'], r'filename=.*%s.*' % slugify(self.task.name)
        )

    def test_only_description_submit(self):
        submit = Submit.objects.create(task=self.task, user=self.user, points=5,
                                       submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
                                       filepath=path.join(path.dirname(__file__), 'test_data', 'submits', 'description.txt'))
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()
        submit_file = helpers.submit_download_filename(submit)

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b''.join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, 'a')

        self.assertIsNone(zipped_file.testzip())
        self.assertIn(submit_file, zipped_file.namelist())
        zipped_file.close()
        f.close()

    def test_only_source_submit(self):
        submit = Submit.objects.create(task=self.task, user=self.user, points=5,
                                       submit_type=submit_constants.SUBMIT_TYPE_SOURCE,
                                       filepath=path.join(path.dirname(__file__), 'test_data', 'submits', 'source.cpp'))
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()

        submit_file = helpers.submit_download_filename(submit)

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b''.join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, 'a')

        self.assertIsNone(zipped_file.testzip())
        # pretoze k nemu nemam description tak nie je co reviewovat
        self.assertNotIn(submit_file, zipped_file.namelist())
        zipped_file.close()
        f.close()

    def test_source_description_submit(self):
        desc_submit = Submit.objects.create(task=self.task, user=self.user, points=5,
                                            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
                                            filepath=path.join(path.dirname(__file__), 'test_data', 'submits', 'description.txt'))
        desc_submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        desc_submit.save()
        submit = Submit.objects.create(task=self.task, user=self.user, points=5,
                                       submit_type=submit_constants.SUBMIT_TYPE_SOURCE,
                                       filepath=path.join(path.dirname(__file__), 'test_data', 'submits', 'source.cpp'))
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()

        submit_file = helpers.submit_source_download_filename(submit, desc_submit.id)

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b''.join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, 'a')

        self.assertIsNone(zipped_file.testzip())
        self.assertIn(submit_file, zipped_file.namelist())
        zipped_file.close()
        f.close()

    def test_comment_in_submit(self):
        comment = '''TESTINGComment\ns diakritikou áäčďéíľňóŕšťúýž'''
        submit = Submit.objects.create(task=self.task, user=self.user, points=5,
                                       submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
                                       filepath=path.join(path.dirname(__file__), 'test_data', 'submits', 'description.txt'))
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()
        Submit.objects.create(task=self.task, user=self.user, points=5,
                              reviewer_comment=comment,
                              testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
                              submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION)

        comm_file = '%s%s' % (helpers.submit_directory(
            submit), review_constants.REVIEW_COMMENT_FILENAME)

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b''.join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, 'a')
        data = zipped_file.read(comm_file)
        self.assertEqual(data.decode('utf-8'), comment)
        zipped_file.close()
        f.close()

    def test_points_in_submit(self):
        points = 47
        submit = Submit.objects.create(task=self.task, user=self.user, points=0,
                                       submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
                                       filepath=path.join(path.dirname(__file__), 'test_data', 'submits', 'description.txt'))
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()
        Submit.objects.create(task=self.task, user=self.user, points=points,
                              testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
                              submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION)

        points_file = '%s%s' % (helpers.submit_directory(
            submit), review_constants.REVIEW_POINTS_FILENAME)

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b''.join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, 'a')
        data = zipped_file.read(points_file)
        self.assertEqual(int(data), points)
        zipped_file.close()
        f.close()

    def test_description_without_file(self):
        submit = Submit.objects.create(task=self.task, user=self.user, points=5,
                                       submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
                                       filepath='')
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b''.join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, 'a')

        data = zipped_file.read(review_constants.REVIEW_ERRORS_FILENAME)
        self.assertIn(self.user.get_full_name(), data.decode('utf-8'))

        zipped_file.close()
        f.close()

    def test_source_description_without_files(self):
        desc_submit = Submit.objects.create(task=self.task, user=self.user, points=5,
                                            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
                                            filepath='')
        desc_submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        desc_submit.save()
        submit = Submit.objects.create(task=self.task, user=self.user, points=5,
                                       submit_type=submit_constants.SUBMIT_TYPE_SOURCE,
                                       filepath='')
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b''.join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, 'a')

        data = zipped_file.read(review_constants.REVIEW_ERRORS_FILENAME)
        self.assertIn(self.user.get_full_name(), data.decode('utf-8'))

        zipped_file.close()
        f.close()


class ReviewEditTest(TestCase):

    def setUp(self):
        year = timezone.now().year + 2
        self.user = User.objects.create_user(username='TestUser', password='password',
                                             first_name='Jozko', last_name='Mrkvicka',
                                             graduation=year)
        self.staff = User.objects.create_user(username='TestStaff', password='password',
                                              first_name='Jozko', last_name='Veduci',
                                              graduation=2014)
        self.staff.is_staff = True
        self.staff.save()

        group = Group.objects.create(name='Test Group')
        group.user_set.add(self.staff)
        competition = Competition.objects.create(name='TestCompetition', organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series 1', year=1,
                                       competition=competition)

        start = timezone.now() + timezone.timedelta(-8)
        end = timezone.now() + timezone.timedelta(-4)
        test_round = Round.objects.create(number=1, series=series, solutions_visible=True,
                                          start_time=start, end_time=end, visible=True)
        self.task = Task.objects.create(number=2, name='Test task 2', round=test_round)
        self.submit = Submit.objects.create(task=self.task, user=self.user, submit_type=1, points=5)
        self.submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        self.submit.save()

        self.url_name = 'admin:review_edit'

    def test_redirect_to_login(self):
        # Najprv sa posle na login, potom na admin login, a az potom na povodnu stranku.
        # Posledna cast za next je double quoted, posledne next je len quoted.
        url = reverse(self.url_name, kwargs={'task_pk': 1, 'submit_pk': 1})
        response = self.client.get(url, follow=True)
        login_url = settings.LOGIN_URL
        admin_login_url = '?next=%s' % reverse('admin:login')
        last_url = quote(url, safe='')
        last_url = quote('?next=%s' % last_url, safe='')
        redirect_to = '%s%s%s' % (login_url, admin_login_url, last_url)
        self.assertRedirects(response, redirect_to)

    def test_redirect_to_admin_login(self):
        # Tato url nie je vobec quoted.
        url = reverse(self.url_name, kwargs={'task_pk': 1, 'submit_pk': 1})
        response = self.client.get(url, follow=True)
        self.client.force_login(self.user)
        response = self.client.get(url)
        redirect_to = '%s?next=%s' % (reverse('admin:login'), url)
        self.assertRedirects(response, redirect_to)

    def test_invalid_task(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={'task_pk': get_noexisting_id(Task),
                                             'submit_pk': get_noexisting_id(Submit)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_not_in_group(self):
        staff = User.objects.create_user(username='TestStaffOther', password='password',
                                         first_name='Jozko', last_name='Veduci',
                                         graduation=2014)
        staff.is_staff = True
        staff.save()
        self.client.force_login(staff)
        url = reverse(self.url_name,
                      kwargs={'task_pk': self.task.id, 'submit_pk': self.submit.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_valid_task(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name,
                      kwargs={'task_pk': self.task.id, 'submit_pk': self.submit.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.name)
        self.assertContains(response, self.user.get_full_name())

    def test_reviewed(self):
        comment = '''TESTINGComment s diakritikou áäčďéíľňóŕšťúýž'''
        self.client.force_login(self.staff)
        url = reverse(self.url_name,
                      kwargs={'task_pk': self.task.id, 'submit_pk': self.submit.id})

        response = self.client.get(url)
        self.assertNotContains(response, comment)

        self.submit.reviewer_comment = comment
        self.submit.save()
        response = self.client.get(url)
        self.assertContains(response, comment)

        multi_line_comment = 'Comment\nOn\nMore\nLines'

        self.submit.reviewer_comment = multi_line_comment
        self.submit.save()
        response = self.client.get(url)
        self.assertContains(response, multi_line_comment)
