# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Entry
from trojsten.people.models import User
from trojsten.news.constants import NEWS_PAGINATE_BY


class NewsTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=settings.SITE_ID)
        self.user = User.objects.create_user(username="TestUser", password="password",
                                             first_name="Jozko", last_name="Mrkvicka",
                                             graduation=2014)

    def test_invalid_news(self):
        url = reverse('news_list', kwargs={'page': 47})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_no_news(self):
        url = reverse('news_list', kwargs={'page': 1})
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Nemáme žiadne novinky")

    def test_one_entry(self):
        entry = Entry.objects.create(author=self.user, title="Test entry", text="Text prispevku.")
        entry.sites.add(self.site)
        url = reverse('news_list', kwargs={'page': 1})
        response = self.client.get(url)
        self.assertContains(response, "Test entry")
        self.assertContains(response, self.user.username)

    def test_edit(self):
        entry = Entry.objects.create(author=self.user, title="Test entry", text="Text prispevku.")
        entry.sites.add(self.site)

        url = reverse('news_list', kwargs={'page': 1})
        response = self.client.get(url)
        # @ToDo: translations
        self.assertNotContains(response, "Upraviť")

        self.client.force_login(self.user)
        url = reverse('news_list', kwargs={'page': 1})
        response = self.client.get(url)
        # @ToDo: translations
        self.assertNotContains(response, "Upraviť")

        staff_user = User.objects.create_user(username="TestStaff", password="password",
                                              first_name="Jozko", last_name="Veduci",
                                              graduation=2014)
        staff_user.is_staff = True
        staff_user.save()

        self.client.force_login(staff_user)
        url = reverse('news_list', kwargs={'page': 1})
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Upraviť")

    def test_tag_entry(self):
        entry = Entry.objects.create(author=self.user, title="Test entry", text="Text prispevku.")
        entry.sites.add(self.site)
        entry.tags.add("TestTAG")
        url = reverse('news_list', kwargs={'page': 1})
        response = self.client.get(url)
        self.assertContains(response, "Test entry")
        self.assertContains(response, "TestTAG")

    def test_two_pages(self):
        paginate_by = NEWS_PAGINATE_BY
        count = paginate_by + 2
        titles = []
        for i in range(count):
            title = "TITLE *%d*" % i
            entry = Entry.objects.create(author=self.user, title=title, text="")
            entry.sites.add(self.site)
            titles.append(title)

        url1 = reverse('news_list', kwargs={'page': 1})
        response1 = self.client.get(url1)
        url2 = reverse('news_list', kwargs={'page': 2})
        response2 = self.client.get(url2)
        for i in range(paginate_by):
            self.assertContains(response1, titles[-i-1])
            self.assertNotContains(response2, titles[-i-1])
        for i in range(paginate_by, count):
            self.assertNotContains(response1, titles[-i-1])
            self.assertContains(response2, titles[-i-1])

        # @ToDo: translations
        self.assertContains(response1, "Strana 1 z")
        # @ToDo: translations
        self.assertContains(response2, "Strana 2 z")

        # @ToDo: translations
        self.assertContains(response1, "Novšie novinky")
        # @ToDo: translations
        self.assertContains(response1, "Staršie novinky")
