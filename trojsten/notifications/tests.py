from django.test import TestCase
from django.utils import timezone
from trojsten.people.models import User
from trojsten.contests.models import Competition, Semester, Round, Task
from trojsten.submit.models import Submit
from django.contrib.sites.models import Site
from django.conf import settings
from django_nyt.models import Subscription, Notification
from trojsten.notifications import constants
from trojsten.submit import constants as submit_constants
from django.urls import reverse


# Create your tests here.
class SubmitTest(TestCase):
    def setUp(self):
        grad_year = timezone.now().year + 1
        self.user = User.objects.create_user(username='jozko',
                                             first_name='Jozko',
                                             last_name='Mrkvicka',
                                             password='pass',
                                             graduation=grad_year)
        self.competition = Competition.objects.create(name='TestCompetition')
        self.competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.start_time_old = timezone.now() + timezone.timedelta(-10)
        self.end_time_new = timezone.now() + timezone.timedelta(10)
        self.semester = Semester.objects.create(number=1,
                                                name='Test semester',
                                                competition=self.competition,
                                                year=1)
        self.round = Round.objects.create(number=1,
                                          semester=self.semester,
                                          visible=True,
                                          solutions_visible=False,
                                          start_time=self.start_time_old,
                                          end_time=self.end_time_new)
        self.task = Task.objects.create(number=1,
                                        name='Test task',
                                        round=self.round,
                                        has_source=True)

    def test_submit_should_subscribe(self):
        submit = Submit(task=self.task,
                        user=self.user,
                        submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
                        points=0,
                        testing_status=submit_constants.SUBMIT_STATUS_IN_QUEUE)
        submit.save()

        self.assertTrue(
            Subscription.objects.filter(
                notification_type__key=constants.NOTIFICATION_SUBMIT_REVIEWED,
                object_id=self.user.pk).exists())

        self.assertTrue(
            Subscription.objects.filter(
                notification_type__key=constants.NOTIFICATION_CONTEST_UPDATED,
                object_id=self.competition.pk).exists())

    def test_submit_should_notify(self):
        submit = Submit(task=self.task,
                        user=self.user,
                        submit_type=submit_constants.SUBMIT_TYPE_DESCRIPTION,
                        points=0,
                        testing_status=submit_constants.SUBMIT_STATUS_IN_QUEUE)
        submit.save()

        submit.testing_status = submit_constants.SUBMIT_STATUS_REVIEWED
        submit.points = 10
        submit.save()

        subscription = Subscription.objects.filter(
            notification_type__key=constants.NOTIFICATION_SUBMIT_REVIEWED,
            object_id=self.user.pk).get()

        query = Notification.objects.filter(subscription=subscription,
                                            user=self.user)

        self.assertTrue(query.exists())

        notification = query.get()
        self.assertIn('10', notification.message)
        self.assertIn(self.task.__str__(), notification.message)
        self.assertEqual(notification.url,
                         reverse("task_submit_page", args=(self.task.pk, )))
