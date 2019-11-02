from django.test import TestCase
from django.utils import timezone

from trojsten.notifications.utils import notify
from trojsten.people.models import User

from .models import Notification, UnsubscribedChannel


class GenericTest(TestCase):
    def setUp(self):
        grad_year = timezone.now().year + 1
        self.user = User.objects.create_user(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=grad_year,
        )
        self.user2 = User.objects.create_user(
            username="jozko2",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=grad_year,
        )

    def test_default(self):
        notify([self.user, self.user2], "foo", "bar", "https://trojsten.sk")

        query = Notification.objects.filter(channel="foo")
        self.assertEquals(query.count(), 2)

    def test_unsubscribed(self):
        UnsubscribedChannel.objects.create(channel="foo", user=self.user)

        notify([self.user, self.user2], "foo", "bar", "https://trojsten.sk")

        query = Notification.objects.filter(channel="foo")
        self.assertEquals(query.count(), 1)
        self.assertEquals(query.get().user, self.user2)
