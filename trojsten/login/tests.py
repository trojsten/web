import json

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

from trojsten.people.models import User


@override_settings(SITE_ID=10, ROOT_URLCONF="trojsten.urls.login")
class LoginViewsTests(TestCase):
    fixtures = ["sites.json"]

    def test_login_root_view_no_login(self):
        url = reverse("login_root_view")
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, "{}?next=/".format(settings.LOGIN_URL))

    def test_login_root_view_login(self):
        u = User.objects.create()
        self.client.force_login(u)
        url = reverse("login_root_view")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


@override_settings(SITE_ID=10, ROOT_URLCONF="trojsten.urls.login")
class ApiTests(TestCase):
    fixtures = ["sites.json"]

    def setUp(self):
        self.user = User.objects.create_user(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            email="jozko@mrkvicka.com",
            password="pass",
            graduation=47,
        )

    def test_current_user_info(self):
        self.client.force_login(self.user)

        response = self.client.get("/api/me").data

        self.assertEquals(response["id"], self.user.id)
        self.assertEquals(response["username"], self.user.username)
        self.assertEquals(response["email"], self.user.email)

    def test_current_user_info_not_logged_in(self):
        response = self.client.get("/api/me").data

        self.assertEquals(response["detail"].code, "not_authenticated")

    def test_is_authenticated(self):
        self.client.force_login(self.user)

        response = json.loads(self.client.get("/api/checklogin").content)

        self.assertTrue(response["authenticated"])

    def test_is_authenticated_not_logged_in(self):
        response = json.loads(self.client.get("/api/checklogin").content)

        self.assertFalse(response["authenticated"])
