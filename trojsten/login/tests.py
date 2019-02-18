# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

from trojsten.people.models import User


@override_settings(
    SITE_ID=10,
    ROOT_URLCONF='trojsten.urls.login',
)
class LoginViewsTests(TestCase):
    fixtures = ['sites.json']

    def test_login_root_view_no_login(self):
        url = reverse('login_root_view')
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '{}?next=/'.format(settings.LOGIN_URL))

    def test_login_root_view_login(self):
        u = User.objects.create()
        self.client.force_login(u)
        url = reverse('login_root_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
