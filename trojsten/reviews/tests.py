#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import shutil
import sys
import tempfile
import zipfile
from os import path

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import formset_factory
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from trojsten.contests.models import Competition, Round, Semester, Task
from trojsten.people.models import User
from trojsten.reviews import constants as review_constants
from trojsten.reviews import helpers
from trojsten.reviews.forms import BasePointForm, BasePointFormSet, UploadZipForm, ZipForm
from trojsten.submit import constants as submit_constants
from trojsten.submit.models import Submit
from trojsten.utils.test_utils import get_noexisting_id

try:
    from urllib.request import quote, unquote
except ImportError:
    from urllib import quote, unquote


class UploadZipFormTests(TestCase):
    def test_only_zip_extension_is_valid(self):
        z = UploadZipForm(data={}, files={"file": SimpleUploadedFile("file.wtf", b"abc")})
        self.assertFalse(z.is_valid())

    def test_zip_extension_check_is_case_insensitive(self):
        z = UploadZipForm(data={}, files={"file": SimpleUploadedFile("file.ZIP", b"abc")})
        self.assertTrue(z.is_valid())

    def test_no_zip_file_uploaded_is_handled_correctly(self):
        z = UploadZipForm(data={}, files={})
        self.assertFalse(z.is_valid())


class ReviewZipFormTests(TestCase):
    def setUp(self):
        self.choices = [(47, "Meno Priezvisko")]
        self.test_str = "ľščťžýáíéúňďôä"
        self.test_str_win1250 = self.test_str.encode("cp1250")
        self.test_str_utf8 = self.test_str.encode("utf8")
        self.valid_files_win1250 = set([self.test_str_win1250])
        self.valid_files_utf8 = set([self.test_str_utf8])
        if sys.version_info[0] == 3:
            # FIXME: remove this check when we stop supporting python2.7
            self.valid_files_win1250 = set([unquote(quote(self.test_str_win1250))])
            self.valid_files_utf8 = set([self.test_str_utf8.decode("utf8")])
        self.user = User(pk=47)
        self.user.save()
        pass

    def test_win_1250_valid(self):
        d = ZipForm(
            {
                "filename": quote(self.test_str_win1250),
                "points": 3,
                "user": 47,
                "comment": self.test_str,
            },
            choices=self.choices,
            max_value=47,
            valid_files=self.valid_files_win1250,
        )
        self.assertTrue(d.is_valid())

    def test_win_1250_encode(self):
        z = ZipForm(
            initial={
                "filename": self.test_str_win1250,
                "points": 3,
                "user": 47,
                "comment": self.test_str_win1250,
            },
            choices=self.choices,
            max_value=47,
            valid_files=self.valid_files_win1250,
        )

        self.assertEqual(z.initial["filename"], quote(self.test_str_win1250))
        self.assertEqual(z.initial["comment"], self.test_str)

    def test_utf8_valid(self):
        d = ZipForm(
            {
                "filename": quote(self.test_str_utf8),
                "points": 3,
                "user": 47,
                "comment": self.test_str,
            },
            choices=self.choices,
            max_value=47,
            valid_files=self.valid_files_utf8,
        )
        self.assertTrue(d.is_valid())

    def test_utf8_encode(self):
        z = ZipForm(
            initial={
                "filename": self.test_str_utf8,
                "points": 3,
                "user": 47,
                "comment": self.test_str_utf8,
            },
            choices=self.choices,
            max_value=47,
            valid_files=self.valid_files_utf8,
        )

        self.assertEqual(z.initial["filename"], quote(self.test_str_utf8))
        self.assertEqual(z.initial["comment"], self.test_str)


class ReviewTest(TestCase):
    def setUp(self):
        year = timezone.now().year + 2
        self.user = User.objects.create_user(
            username="TestUser",
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=year,
        )
        self.staff = User.objects.create_user(
            username="TestStaff",
            password="password",
            first_name="Jozko",
            last_name="Veduci",
            graduation=2014,
        )
        self.staff.is_staff = True
        self.staff.save()

        group = Group.objects.create(name="Test Group")
        group.user_set.add(self.staff)
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(
            number=1, name="Test semester 1", year=1, competition=competition
        )

        start = timezone.now() + timezone.timedelta(-8)
        end = timezone.now() + timezone.timedelta(-4)
        test_round = Round.objects.create(
            number=1,
            semester=semester,
            solutions_visible=True,
            start_time=start,
            end_time=end,
            visible=True,
        )
        self.no_submit_task = Task.objects.create(number=1, name="Test task 1", round=test_round)
        self.task = Task.objects.create(number=2, name="Test task 2", round=test_round)
        self.submit = Submit.objects.create(task=self.task, user=self.user, submit_type=1, points=5)
        self.submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        self.submit.save()

        self.url_name = "admin:review_task"

    def test_redirect_to_login(self):
        # Najprv sa posle na login, potom na admin login, a az potom na povodnu stranku.
        # Posledna cast za next je double quoted, posledne next je len quoted.
        url = reverse(self.url_name, kwargs={"task_pk": 1})
        response = self.client.get(url)
        redirect_to = "%s?next=%s" % (reverse("admin:login"), url)
        self.assertRedirects(response, redirect_to, fetch_redirect_response=False)

    def test_redirect_to_admin_login(self):
        # Tato url nie je vobec quoted.
        url = reverse(self.url_name, kwargs={"task_pk": 1})
        response = self.client.get(url, follow=True)
        self.client.force_login(self.user)
        response = self.client.get(url)
        redirect_to = "%s?next=%s" % (reverse("admin:login"), url)
        self.assertRedirects(response, redirect_to)

    def test_invalid_task(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": get_noexisting_id(Task)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_not_in_group(self):
        staff = User.objects.create_user(
            username="TestStaffOther",
            password="password",
            first_name="Jozko",
            last_name="Veduci",
            graduation=2014,
        )
        staff.is_staff = True
        staff.save()
        self.client.force_login(staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.no_submit_task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_valid_task(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.no_submit_task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.no_submit_task.name)

    def test_not_reviewable_submit(self):
        for s_type in [
            submit_constants.SUBMIT_TYPE_SOURCE,
            submit_constants.SUBMIT_TYPE_TESTABLE_ZIP,
            submit_constants.SUBMIT_TYPE_EXTERNAL,
        ]:
            submit = Submit.objects.create(
                task=self.no_submit_task, user=self.user, submit_type=s_type, points=5
            )
            submit.time = self.no_submit_task.round.start_time + timezone.timedelta(0, 5)
            submit.save()
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.no_submit_task.id})
        response = self.client.get(url)
        self.assertNotContains(response, self.user.get_full_name())

    def test_description_submit(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})
        response = self.client.get(url)
        self.assertContains(response, self.user.get_full_name())

    def test_reviewed(self):
        comment = "TESTINGcomment"
        multi_line_comment = """Comment
        On
        More
        Lines"""
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})

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

    def test_hidden_points_alert(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})
        self.task.description_points_visible = False
        self.task.save()

        response = self.client.get(url)
        self.assertContains(response, _("Description points are hidden in results!"))

        self.task.description_points_visible = True
        self.task.save()

        response = self.client.get(url)
        self.assertNotContains(response, _("Description points are hidden in results!"))

    def test_submitted_at_end_of_round(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})

        submit = Submit.objects.create(task=self.task, user=self.user, submit_type=1, points=5)
        submit.time = self.task.round.end_time
        submit.save()

        response = self.client.get(url)
        self.assertContains(response, self.user.get_full_name())


@override_settings(SUBMIT_PATH=tempfile.mkdtemp(dir=path.join(path.dirname(__file__), "test_data")))
class DownloadLatestSubmits(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.SUBMIT_PATH)
        super(DownloadLatestSubmits, cls).tearDownClass()

    def setUp(self):
        year = timezone.now().year + 2
        self.user = User.objects.create_user(
            username="TestUser",
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=year,
        )
        self.staff = User.objects.create_user(
            username="TestStaff",
            password="password",
            first_name="Jozko",
            last_name="Veduci",
            graduation=2014,
        )
        self.staff.is_staff = True
        self.staff.save()
        self.protocol = """<protokol><runLog>
        <test><name>0.sample.a.in</name><resultCode>1</resultCode><resultMsg>OK</resultMsg><time>28</time></test>
        <test><name>0.sample.b.in</name><resultCode>1</resultCode><resultMsg>OK</resultMsg><time>28</time></test>
        <score>100</score><details>
        Score: 100
        </details><finalResult>1</finalResult><finalMessage>OK (OK: 100 %)</finalMessage>
        </runLog></protokol>
        """

        group = Group.objects.create(name="Test Group")
        group.user_set.add(self.staff)
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(
            number=1, name="Test semester 1", year=1, competition=competition
        )

        test_round = Round.objects.create(
            number=1, semester=semester, solutions_visible=True, visible=True
        )
        self.task = Task.objects.create(number=2, name="TestTask2", round=test_round)

        self.url_name = "admin:download_latest_submits"

    def test_redirect_to_login(self):
        # Should send user to administrator login
        url = reverse(self.url_name, kwargs={"task_pk": 1})
        response = self.client.get(url)
        redirect_to = "%s?next=%s" % (reverse("admin:login"), url)
        self.assertRedirects(response, redirect_to, fetch_redirect_response=False)

    def test_redirect_to_admin_login(self):
        # Tato url nie je vobec quoted.
        url = reverse(self.url_name, kwargs={"task_pk": 1})
        response = self.client.get(url, follow=True)
        self.client.force_login(self.user)
        response = self.client.get(url)
        redirect_to = "%s?next=%s" % (reverse("admin:login"), url)
        self.assertRedirects(response, redirect_to)

    def test_invalid_task(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": get_noexisting_id(Task)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_not_in_group(self):
        staff = User.objects.create_user(
            username="TestStaffOther",
            password="password",
            first_name="Jozko",
            last_name="Veduci",
            graduation=2014,
        )
        staff.is_staff = True
        staff.save()
        self.client.force_login(staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_valid_task(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertRegexpMatches(
            response["Content-Disposition"], r"filename=.*%s.*" % slugify(self.task.name)
        )

    def test_only_description_submit(self):
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=5,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            filepath=path.join(path.dirname(__file__), "test_data", "submits", "description.txt"),
        )
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()
        submit_file = helpers.submit_download_filename(submit, 0)

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b"".join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, "a")

        self.assertIsNone(zipped_file.testzip())
        self.assertIn(submit_file, zipped_file.namelist())
        zipped_file.close()
        f.close()

    def test_only_source_submit(self):
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=5,
            submit_type=submit_constants.SUBMIT_TYPE_SOURCE,
            filepath=path.join(path.dirname(__file__), "test_data", "submits", "source.cpp"),
        )
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()

        submit_file = helpers.submit_download_filename(submit, 0)

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b"".join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, "a")

        self.assertIsNone(zipped_file.testzip())
        # pretoze k nemu nemam description tak nie je co reviewovat
        self.assertNotIn(submit_file, zipped_file.namelist())
        zipped_file.close()
        f.close()

    def test_source_description_submit(self):
        desc_submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=5,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            filepath=path.join(path.dirname(__file__), "test_data", "submits", "description.txt"),
        )
        desc_submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        desc_submit.save()
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=5,
            submit_type=submit_constants.SUBMIT_TYPE_SOURCE,
            filepath=path.join(path.dirname(__file__), "test_data", "submits", "source.cpp"),
            protocol=self.protocol,
            protocol_id="test_id_47",
        )
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()

        submit_file = helpers.submit_source_download_filename(submit, desc_submit.id, 0)
        protocol_file = helpers.submit_protocol_download_filename(submit, desc_submit.id, 0)

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b"".join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, "a")

        self.assertIsNone(zipped_file.testzip())
        self.assertIn(submit_file, zipped_file.namelist())
        self.assertIn(protocol_file, zipped_file.namelist())
        zipped_file.close()
        f.close()

    def test_comment_in_submit(self):
        comment = """TESTINGComment\ns diakritikou áäčďéíľňóŕšťúýž"""
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=5,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            filepath=path.join(path.dirname(__file__), "test_data", "submits", "description.txt"),
        )
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()
        Submit.objects.create(
            task=self.task,
            user=self.user,
            points=5,
            reviewer_comment=comment,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
        )

        comm_file = "%s%s" % (
            helpers.submit_directory(submit, 0),
            review_constants.REVIEW_COMMENT_FILENAME,
        )

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b"".join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, "a")
        data = zipped_file.read(comm_file)
        self.assertEqual(data.decode("utf-8"), comment)
        zipped_file.close()
        f.close()

    def test_points_in_submit(self):
        points = 47
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=0,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            filepath=path.join(path.dirname(__file__), "test_data", "submits", "description.txt"),
        )
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()
        Submit.objects.create(
            task=self.task,
            user=self.user,
            points=points,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
        )

        points_file = "%s%s" % (
            helpers.submit_directory(submit, 0),
            review_constants.REVIEW_POINTS_FILENAME,
        )

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b"".join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, "a")
        data = zipped_file.read(points_file)
        self.assertEqual(int(data), points)
        zipped_file.close()
        f.close()

    def test_description_without_file(self):
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=5,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            filepath="",
        )
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b"".join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, "a")

        data = zipped_file.read(review_constants.REVIEW_ERRORS_FILENAME)
        self.assertIn(self.user.get_full_name(), data.decode("utf-8"))

        zipped_file.close()
        f.close()

    def test_source_description_without_files(self):
        desc_submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=5,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            filepath="",
        )
        desc_submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        desc_submit.save()
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=5,
            submit_type=submit_constants.SUBMIT_TYPE_SOURCE,
            filepath="",
        )
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b"".join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, "a")

        data = zipped_file.read(review_constants.REVIEW_ERRORS_FILENAME)
        self.assertIn(self.user.get_full_name(), data.decode("utf-8"))

        zipped_file.close()
        f.close()

    def test_exclude_review_in_download_latest_submits(self):
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=0,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            filepath=path.join(path.dirname(__file__), "test_data", "submits", "description.txt"),
        )
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()
        submit_file = helpers.submit_download_filename(submit, 0)

        review = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=5,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            filepath=path.join(path.dirname(__file__), "test_data", "submits", "review.txt"),
        )
        review_file = helpers.submit_download_filename(review, 0)

        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b"".join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, "a")

        self.assertIsNone(zipped_file.testzip())
        self.assertIn(submit_file, zipped_file.namelist())
        self.assertNotIn(review_file, zipped_file.namelist())
        zipped_file.close()
        f.close()

    def test_include_review_in_download_latest_reviewed_submits(self):
        submit = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=0,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            filepath=path.join(path.dirname(__file__), "test_data", "submits", "description.txt"),
        )
        submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        submit.save()
        submit_file = helpers.submit_download_filename(submit, 0)

        review = Submit.objects.create(
            task=self.task,
            user=self.user,
            points=5,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            filepath=path.join(path.dirname(__file__), "test_data", "submits", "review.txt"),
        )
        review_file = helpers.submit_download_filename(review, 0)

        self.client.force_login(self.staff)
        url = reverse("admin:download_latest_reviewed_submits", kwargs={"task_pk": self.task.id})
        response = self.client.get(url)
        f = io.BytesIO(b"".join(response.streaming_content))
        zipped_file = zipfile.ZipFile(f, "a")

        self.assertIsNone(zipped_file.testzip())
        self.assertNotIn(submit_file, zipped_file.namelist())
        self.assertIn(review_file, zipped_file.namelist())
        zipped_file.close()
        f.close()


class ReviewEditTest(TestCase):
    def setUp(self):
        year = timezone.now().year + 2
        self.user = User.objects.create_user(
            username="TestUser",
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=year,
        )
        self.staff = User.objects.create_user(
            username="TestStaff",
            password="password",
            first_name="Jozko",
            last_name="Veduci",
            graduation=2014,
        )
        self.staff.is_staff = True
        self.staff.save()

        group = Group.objects.create(name="Test Group")
        group.user_set.add(self.staff)
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(
            number=1, name="Test semester 1", year=1, competition=competition
        )

        start = timezone.now() + timezone.timedelta(-8)
        end = timezone.now() + timezone.timedelta(-4)
        test_round = Round.objects.create(
            number=1,
            semester=semester,
            solutions_visible=True,
            start_time=start,
            end_time=end,
            visible=True,
        )
        self.task = Task.objects.create(number=2, name="Test task 2", round=test_round)
        self.submit = Submit.objects.create(task=self.task, user=self.user, submit_type=1, points=5)
        self.submit.time = self.task.round.start_time + timezone.timedelta(0, 5)
        self.submit.save()

        self.url_name = "admin:review_edit"

    def test_redirect_to_login(self):
        # Should send user to administrator login
        url = reverse(self.url_name, kwargs={"task_pk": 1, "submit_pk": 1})
        response = self.client.get(url)
        redirect_to = "%s?next=%s" % (reverse("admin:login"), url)
        self.assertRedirects(response, redirect_to, fetch_redirect_response=False)

    def test_redirect_to_admin_login(self):
        # Tato url nie je vobec quoted.
        url = reverse(self.url_name, kwargs={"task_pk": 1, "submit_pk": 1})
        response = self.client.get(url, follow=True)
        self.client.force_login(self.user)
        response = self.client.get(url)
        redirect_to = "%s?next=%s" % (reverse("admin:login"), url)
        self.assertRedirects(response, redirect_to)

    def test_invalid_task(self):
        self.client.force_login(self.staff)
        url = reverse(
            self.url_name,
            kwargs={"task_pk": get_noexisting_id(Task), "submit_pk": get_noexisting_id(Submit)},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_not_in_group(self):
        staff = User.objects.create_user(
            username="TestStaffOther",
            password="password",
            first_name="Jozko",
            last_name="Veduci",
            graduation=2014,
        )
        staff.is_staff = True
        staff.save()
        self.client.force_login(staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id, "submit_pk": self.submit.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_valid_task(self):
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id, "submit_pk": self.submit.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.name)
        self.assertContains(response, self.user.get_full_name())

    def test_reviewed(self):
        comment = """TESTINGComment s diakritikou áäčďéíľňóŕšťúýž"""
        self.client.force_login(self.staff)
        url = reverse(self.url_name, kwargs={"task_pk": self.task.id, "submit_pk": self.submit.id})

        response = self.client.get(url)
        self.assertNotContains(response, comment)

        self.submit.reviewer_comment = comment
        self.submit.save()
        response = self.client.get(url)
        self.assertContains(response, comment)

        multi_line_comment = "Comment\nOn\nMore\nLines"

        self.submit.reviewer_comment = multi_line_comment
        self.submit.save()
        response = self.client.get(url)
        self.assertContains(response, multi_line_comment)


class PointFormSetTests(TestCase):
    def setUp(self):
        year = timezone.now().year + 2
        self.user1 = User.objects.create_user(
            username="TestUser1",
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=year,
            pk=1,
        )
        group = Group.objects.create(name="Test Group")
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(
            number=1, name="Test semester 1", year=1, competition=competition
        )

        test_round = Round.objects.create(
            number=1,
            semester=semester,
            solutions_visible=True,
            visible=True,
            start_time=timezone.now() + timezone.timedelta(-4),
            end_time=timezone.now() + timezone.timedelta(-1),
        )
        self.task = Task.objects.create(
            number=2, name="TestTask2", round=test_round, description_points=9
        )
        submit = Submit.objects.create(
            task=self.task,
            user=self.user1,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            points=0,
            testing_status=submit_constants.SUBMIT_STATUS_IN_QUEUE,
        )
        submit.time = test_round.end_time + timezone.timedelta(hours=-1)
        submit.save()
        self.form_set_class = formset_factory(BasePointForm, BasePointFormSet, extra=0)
        self.data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-user": "1",
            "form-0-points": "",
            "form-0-reviewer_comment": "",
        }

    def test_add_new_reviews(self):
        self.data["form-0-points"] = 4
        self.data["form-0-reviewer_comment"] = "Nic moc"
        form_set = self.form_set_class(
            self.data, form_kwargs={"max_points": self.task.description_points}
        )
        self.assertTrue(form_set.is_valid())
        form_set.save(self.task)
        users = helpers.get_latest_submits_for_task(self.task)
        self.assertEqual(users[self.user1]["review"].points, 4)
        self.assertEqual(users[self.user1]["review"].reviewer_comment, "Nic moc")

    def test_edit_review(self):
        Submit.objects.create(
            task=self.task,
            user=self.user1,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            points=7,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            reviewer_comment="First comment",
        )
        self.data["form-0-points"] = 9
        self.data["form-0-reviewer_comment"] = "Second comment"
        form_set = self.form_set_class(
            self.data, form_kwargs={"max_points": self.task.description_points}
        )
        self.assertTrue(form_set.is_valid())
        form_set.save(self.task)
        users = helpers.get_latest_submits_for_task(self.task)
        self.assertEqual(users[self.user1]["review"].points, 9)
        self.assertEqual(users[self.user1]["review"].reviewer_comment, "Second comment")

    def test_empty_points(self):
        form_set = self.form_set_class(
            self.data, form_kwargs={"max_points": self.task.description_points}
        )
        self.assertTrue(form_set.is_valid())
        form_set.save(self.task)
        users = helpers.get_latest_submits_for_task(self.task)
        self.assertNotIn("review", users[self.user1])

    def test_empty_points_with_review(self):
        Submit.objects.create(
            task=self.task,
            user=self.user1,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            points=7,
            testing_status=submit_constants.SUBMIT_STATUS_REVIEWED,
            reviewer_comment="First comment",
        )
        form_set = self.form_set_class(
            self.data, form_kwargs={"max_points": self.task.description_points}
        )
        self.assertTrue(form_set.is_valid())
        form_set.save(self.task)
        users = helpers.get_latest_submits_for_task(self.task)
        self.assertNotIn("review", users[self.user1])

    def test_invalid_negative_points(self):
        self.data["form-0-points"] = -47
        form_set = self.form_set_class(
            self.data, form_kwargs={"max_points": self.task.description_points}
        )
        self.assertFalse(form_set.is_valid())

    def test_invalid_too_many_points(self):
        self.data["form-0-points"] = 47
        form_set = self.form_set_class(
            self.data, form_kwargs={"max_points": self.task.description_points}
        )
        self.assertFalse(form_set.is_valid())


class ZIPUploadTests(TestCase):
    def setUp(self):
        year = timezone.now().year + 2
        self.user1 = User.objects.create_user(
            username="TestUser1",
            password="password",
            first_name="Jozko",
            last_name="Mrkvicka",
            graduation=year,
            pk=1,
        )
        self.staff = User.objects.create_user(
            username="TestStaff",
            password="password",
            first_name="Jozko",
            last_name="Veduci",
            graduation=2014,
            pk=2,
        )
        self.staff.is_staff = True
        self.staff.save()

        group = Group.objects.create(name="Test Group")
        group.user_set.add(self.staff)
        competition = Competition.objects.create(name="TestCompetition", organizers_group=group)
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        semester = Semester.objects.create(
            number=1, name="Test semester 1", year=1, competition=competition
        )

        test_round = Round.objects.create(
            number=1,
            semester=semester,
            solutions_visible=True,
            visible=True,
            start_time=timezone.now() + timezone.timedelta(-4),
            end_time=timezone.now() + timezone.timedelta(-1),
        )
        self.task = Task.objects.create(
            number=2, name="TestTask2", round=test_round, description_points=9
        )

        submit = Submit.objects.create(
            pk=1,
            task=self.task,
            user=self.user1,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            points=0,
            testing_status=submit_constants.SUBMIT_STATUS_IN_QUEUE,
        )
        submit.time = test_round.end_time + timezone.timedelta(hours=-1)
        submit.save()

    def test_upload(self):
        self.client.force_login(self.staff)
        with open(path.join(path.dirname(__file__), "test_data", "zip_all.zip"), "rb") as zip:
            response = self.client.post(
                reverse("admin:review_task", kwargs={"task_pk": self.task.id}),
                {"Upload": "Upload", "file": zip},
                follow=True,
            )

            self.assertContains(response, "Super riesenie!")
            self.assertContains(response, "11")
            self.assertContains(response, "0123.pdf")
            self.assertNotContains(response, "Thumbs.db")
