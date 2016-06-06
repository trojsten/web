# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase
from wiki.models import Article, ArticleRevision, URLPath

from trojsten.contests.models import Competition, Round, Series
from trojsten.people.models import User


class ArchiveTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=settings.SITE_ID)

        root_article = Article.objects.create()
        ArticleRevision.objects.create(article=root_article, title="test 1")
        urlpath_root = URLPath.objects.create(site=self.site, article=root_article)
        archive_article = Article.objects.create()
        ArticleRevision.objects.create(article=archive_article, title="test 2")
        URLPath.objects.create(site=self.site, article=archive_article, slug="archiv",
                               parent=urlpath_root)

        self.url = reverse('archive')

    def test_no_competitions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # @ToDo: translations
        self.assertContains(response, "Ešte nie sú žiadne súťaže.")

    def test_no_rounds(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(self.site)
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "Ešte nie sú žiadne kolá.")

    def test_one_year(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(self.site)
        series = Series.objects.create(number=1, name='Test series', competition=competition,
                                       year=1)
        Round.objects.create(number=1, series=series, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "1. ročník")
        # @ToDo: translations
        self.assertContains(response, "1. séria")
        # @ToDo: translations
        self.assertContains(response, "1. kolo")
        # @ToDo: translations
        self.assertContains(response, "Zadania a vzoráky")
        # @ToDo: translations
        self.assertContains(response, "Výsledky")

    def test_two_competitions(self):
        competition1 = Competition.objects.create(name='TestCompetition 42')
        competition1.sites.add(self.site)

        response = self.client.get(self.url)
        self.assertContains(response, "TestCompetition 42")
        self.assertNotContains(response, "TestCompetition 47")

        competition2 = Competition.objects.create(name='TestCompetition 47')
        competition2.sites.add(self.site)

        response = self.client.get(self.url)
        self.assertContains(response, "TestCompetition 47")

        series1 = Series.objects.create(number=42, name='Test series 42', competition=competition1,
                                        year=42)
        series2 = Series.objects.create(number=47, name='Test series 47', competition=competition2,
                                        year=47)
        Round.objects.create(number=42, series=series1, solutions_visible=True, visible=True)
        Round.objects.create(number=47, series=series2, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "42. ročník")
        # @ToDo: translations
        self.assertContains(response, "47. ročník")
        # @ToDo: translations
        self.assertContains(response, "42. séria")
        # @ToDo: translations
        self.assertContains(response, "47. séria")
        # @ToDo: translations
        self.assertContains(response, "42. kolo")
        # @ToDo: translations
        self.assertContains(response, "47. kolo")

    def test_two_years(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(self.site)
        series1 = Series.objects.create(number=1, name='Test series 1', competition=competition,
                                        year=1)
        series2 = Series.objects.create(number=1, name='Test series 2', competition=competition,
                                        year=2)
        Round.objects.create(number=1, series=series1, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "1. ročník")
        # @ToDo: translations
        self.assertNotContains(response, "2. ročník")

        Round.objects.create(number=1, series=series2, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "2. ročník")

    def test_two_series(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(self.site)
        series1 = Series.objects.create(number=1, name='Test series 1', competition=competition,
                                        year=1)
        series2 = Series.objects.create(number=2, name='Test series 2', competition=competition,
                                        year=1)
        Round.objects.create(number=1, series=series1, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "1. séria")
        # @ToDo: translations
        self.assertNotContains(response, "2. séria")

        Round.objects.create(number=1, series=series2, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "2. séria")

    def test_two_rounds(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(self.site)
        series = Series.objects.create(number=1, name='Test series 1', competition=competition,
                                       year=1)
        Round.objects.create(number=1, series=series, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "1. kolo")
        # @ToDo: translations
        self.assertNotContains(response, "2. kolo")

        Round.objects.create(number=2, series=series, solutions_visible=True, visible=True)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "2. kolo")

    def test_invisible_rounds(self):
        group = Group.objects.create(name="Test Group")
        competition = Competition.objects.create(name='TestCompetition', organizers_group=group)
        competition.sites.add(self.site)
        series = Series.objects.create(number=1, name='Test series 1', competition=competition,
                                       year=1)
        Round.objects.create(number=1, series=series, solutions_visible=True, visible=False)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertNotContains(response, "1. kolo")

        user = User.objects.create_user(username="TestUser", password="password",
                                        first_name="Arasid", last_name="Mrkvicka", graduation=2014)
        group.user_set.add(user)
        self.client.force_login(user)
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, "1. kolo")
        # @ToDo: translations
        self.assertContains(response, "skryté")
