from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils import timezone

from trojsten.contests.models import Competition, Round, Semester, Task
from trojsten.notifications.constants import SubscriptionStatus
from trojsten.people.models import User
from trojsten.submit import constants as submit_constants
from trojsten.submit.models import Submit

from .models import Notification, Subscription
from .notification_types import RoundStarted, SubmitReviewed


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

    def test_submit_should_subscribe(self):
        submit = Submit(
            task=self.task,
            user=self.user,
            submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
            points=0,
            testing_status=submit_constants.SUBMIT_STATUS_IN_QUEUE,
        )
        submit.save()

        self.assertTrue(
            Subscription.objects.filter(
                notification_type=SubmitReviewed().database_key, object_id=self.user.pk
            ).exists()
        )

        self.assertTrue(
            Subscription.objects.filter(
                notification_type=RoundStarted().database_key, object_id=self.competition.pk
            ).exists()
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

        subscription = Subscription.objects.filter(
            user=self.user, notification_type=SubmitReviewed().database_key, object_id=self.user.pk
        ).get()

        query = Notification.objects.filter(subscription=subscription)

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

        subscription = RoundStarted(self.competition).subscribe(self.user)

        round.visible = False
        round.save()

        self.assertFalse(Notification.objects.filter(subscription=subscription).exists())

    def test_update_invisible_to_visible(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=False,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )

        subscription = RoundStarted(self.competition).subscribe(self.user)

        round.visible = True
        round.save()

        self.assertTrue(Notification.objects.filter(subscription=subscription).exists())

    def test_update_visible_to_visible(self):
        round = Round.objects.create(
            number=1,
            semester=self.semester,
            visible=False,
            solutions_visible=False,
            start_time=self.start_time_old,
            end_time=self.end_time_new,
        )

        subscription = RoundStarted(self.competition).subscribe(self.user)

        round.visible = True
        round.save()

        round.visible = True
        round.save()

        query = Notification.objects.filter(subscription=subscription)

        self.assertTrue(query.exists())
        self.assertEqual(query.count(), 1)


class NotificationTypeTest(TestCase):
    def setUp(self):
        grad_year = timezone.now().year + 1
        self.user = User.objects.create_user(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=grad_year,
        )

    def test_subscribe_unsubscribe(self):
        notification_type = SubmitReviewed(self.user)

        notification_type.subscribe(self.user)
        self.assertTrue(
            Subscription.objects.filter(
                notification_type=notification_type.database_key,
                user=self.user,
                status=SubscriptionStatus.SUBSCRIBED,
            ).exists()
        )

        notification_type.unsubscribe(self.user)
        self.assertTrue(
            Subscription.objects.filter(
                notification_type=notification_type.database_key,
                user=self.user,
                status=SubscriptionStatus.UNSUBSCRIBED,
            ).exists()
        )

    def test_subscribe_unless_unsubscribed(self):
        notification_type = SubmitReviewed(self.user)

        notification_type.unsubscribe(self.user)
        self.assertTrue(
            Subscription.objects.filter(
                notification_type=notification_type.database_key,
                user=self.user,
                status=SubscriptionStatus.UNSUBSCRIBED,
            ).exists()
        )

        notification_type.subscribe_unless_unsubscibed(self.user)
        self.assertFalse(
            Subscription.objects.filter(
                notification_type=notification_type.database_key,
                user=self.user,
                status=SubscriptionStatus.SUBSCRIBED,
            ).exists()
        )
