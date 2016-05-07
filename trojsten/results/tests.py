# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase

from trojsten.contests.models import Competition, Round, Series
from trojsten.tasks.models import Submit
from trojsten.tasks.models import Task
from trojsten.people.models import User


class RecentResultsTest(TestCase):
    def setUp(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.series = Series.objects.create(number=1, name='Test series', competition=competition, year=1)
        self.url = reverse('view_latest_results')
        self.user = User.objects.create(username="TestUser", password="password", first_name="Jozko", last_name="Mrkvicka", graduation=2017)

    def test_no_rounds(self):
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, 'Ešte nebeží žiadne kolo.')

    def test_one_round(self):
        start = datetime.datetime.now() + datetime.timedelta(-4)
        end = datetime.datetime.now() + datetime.timedelta(4)
        test_round = Round.objects.create(number=1, series=self.series, visible=True, solutions_visible=True, start_time=start, end_time=end)
        task = Task.objects.create(number=1, name='Test task 1', round=test_round)
        Submit.objects.create(task=task, time=datetime.datetime.now(), user=self.user, submit_type=0, points=5)

        response = self.client.get(self.url)
        self.assertContains(response, 'Jozko Mrkvicka')

    def test_two_rounds(self):
        start1 = datetime.datetime.strptime('13 7 2013', '%d %m %Y')
        end1 = datetime.datetime.strptime('13 8 2013', '%d %m %Y')
        start2 = datetime.datetime.strptime('13 9 2013', '%d %m %Y')
        end2 = datetime.datetime.strptime('13 10 2013', '%d %m %Y')
        submit_time = datetime.datetime.strptime('12 8 2013', '%d %m %Y')
        round1 = Round.objects.create(number=1, series=self.series, visible=True, solutions_visible=True, start_time=start1, end_time=end1)
        Round.objects.create(number=1, series=self.series, visible=True, solutions_visible=True, start_time=start2, end_time=end2)
        task1 = Task.objects.create(number=1, name='Test task 1', round=round1)
        Submit.objects.create(task=task1, time=submit_time, user=self.user, submit_type=0, points=5)

        response = self.client.get(self.url)
        self.assertNotContains(response, 'Jozko Mrkvicka')
        # @ToDo: translations
        self.assertContains(response, 'Žiadne submity')

    def test_closed_round(self):
        start = datetime.datetime.now() + datetime.timedelta(-8)
        end = datetime.datetime.now() + datetime.timedelta(-4)
        Round.objects.create(number=1, series=self.series, visible=True, solutions_visible=True, start_time=start, end_time=end)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, 'Výsledky sú predbežné.')
