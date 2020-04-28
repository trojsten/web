from django.test import TestCase
from django.urls import reverse
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

    def test_read_all(self):
        notify([self.user], "foo", "msg", "https://trojsten.sk")
        notify([self.user], "foo", "msg2", "https://trojsten.sk")
        notify([self.user2], "foo", "msg2", "https://trojsten.sk")

        response = self.client.post(reverse("notification_read_all"))
        self.assertEqual(response.status_code, 302)

        self.assertEquals(Notification.objects.filter(channel="foo", was_read=False).count(), 3)

        self.client.force_login(self.user)
        response = self.client.post(reverse("notification_read_all"))
        self.assertEqual(response.status_code, 200)
        query = Notification.objects.filter(channel="foo", was_read=False)
        self.assertEquals(query.count(), 1)
        self.assertEquals(query.get().user, self.user2)
