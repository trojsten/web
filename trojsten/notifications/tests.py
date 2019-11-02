from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils import timezone

from trojsten.contests.models import Competition, Round, Semester, Task
from trojsten.people.models import User
from trojsten.submit import constants as submit_constants
from trojsten.submit.models import Submit

from .models import Notification


class SubmitTest(TestCase):
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
        self.task = Task.objects.create(
            number=1, name="Test task", round=self.round, has_source=True
        )

    def test_submit_should_notify(self):
        submit = Submit(
            task=self.task,
            user=self.user,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            points=0,
            testing_status=submit_constants.SUBMIT_STATUS_IN_QUEUE,
        )
        submit.save()

        submit.testing_status = submit_constants.SUBMIT_STATUS_REVIEWED
        submit.points = 10
        submit.save()

        query = Notification.objects.filter(channel="submit_reviewed")
        self.assertTrue(query.exists())


class ContestTest(TestCase):
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
