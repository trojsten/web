# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# import timezone

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from trojsten.contests.models import Competition, Round, Semester
from trojsten.people.models import User
from trojsten.submit.models import Submit
from trojsten.contests.models import Task
from trojsten.utils.test_utils import get_noexisting_id


class RecentResultsTest(TestCase):
    def setUp(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.semester = Semester.objects.create(number=1, name='Test semester', competition=competition,
                                            year=1)
        self.url = reverse('view_latest_results')
        year = timezone.now().year + 2
        self.user = User.objects.create(username="TestUser", password="password",
                                        first_name="Jozko", last_name="Mrkvicka", graduation=year)

    def test_no_rounds(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # @ToDo: translations
        self.assertContains(response, 'Ešte nebeží žiadne kolo.')

    def test_rounds(self):
        start1 = timezone.now() + timezone.timedelta(-8)
        end1 = timezone.now() + timezone.timedelta(-4)
        start2 = timezone.now() + timezone.timedelta(-4)
        end2 = timezone.now() + timezone.timedelta(4)
        round1 = Round.objects.create(number=1, semester=self.semester, visible=True,
                                      solutions_visible=True, start_time=start1, end_time=end1)
        round2 = Round.objects.create(number=2, semester=self.semester, visible=True, start_time=start2,
                                      end_time=end2, solutions_visible=True)
        task1 = Task.objects.create(number=1, name='Test task 1', round=round1)
        task2 = Task.objects.create(number=1, name='Test task 2', round=round2)

        submit = Submit.objects.create(task=task1, user=self.user, submit_type=0, points=5)
        submit.time = start1 + timezone.timedelta(0, 5)
        submit.save()

        response = self.client.get("%s?single_round=True" % self.url)
        self.assertNotContains(response, self.user.get_full_name())
        # @ToDo: translations
        self.assertContains(response, 'Žiadne submity')

        submit = Submit.objects.create(task=task2, user=self.user, submit_type=0, points=5)
        submit.time = start2 + timezone.timedelta(0, 5)
        submit.save()

        response = self.client.get("%s?single_round=True" % self.url)
        self.assertContains(response, self.user.get_full_name())

    def test_closed_round(self):
        start = timezone.now() + timezone.timedelta(-8)
        end = timezone.now() + timezone.timedelta(-4)
        Round.objects.create(number=1, semester=self.semester, visible=True, solutions_visible=True,
                             start_time=start, end_time=end)

        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, 'Výsledky sú predbežné.')

    def test_old_user(self):
        old_user = User.objects.create(username="TestOldUser", password="password",
                                       first_name="Jozko", last_name="Starcek", graduation=2010)
        start = timezone.now() + timezone.timedelta(-4)
        end = timezone.now() + timezone.timedelta(4)
        test_round = Round.objects.create(number=1, semester=self.semester, visible=True,
                                          solutions_visible=True, start_time=start, end_time=end)
        task = Task.objects.create(number=1, name='Test task 1', round=test_round)

        submit = Submit.objects.create(task=task, user=old_user, submit_type=0, points=5)
        submit.time = start + timezone.timedelta(0, 5)
        submit.save()

        response = self.client.get(self.url)
        self.assertNotContains(response, old_user.get_full_name())

        response = self.client.get("%s?show_staff=True" % self.url)
        self.assertContains(response, old_user.get_full_name())


class ResultsTest(TestCase):
    def setUp(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        self.semester1 = Semester.objects.create(number=1, name='Test semester 1', year=1,
                                             competition=competition)
        self.semester2 = Semester.objects.create(number=2, name='Test semester 2', year=1,
                                             competition=competition)

        start1 = timezone.now() + timezone.timedelta(-12)
        end1 = timezone.now() + timezone.timedelta(-8)
        start2 = timezone.now() + timezone.timedelta(-8)
        end2 = timezone.now() + timezone.timedelta(-4)
        start3 = timezone.now() + timezone.timedelta(-4)
        end3 = timezone.now() + timezone.timedelta(4)
        self.round1 = Round.objects.create(number=1, semester=self.semester1, solutions_visible=True,
                                           start_time=start1, end_time=end1, visible=True)
        self.round2 = Round.objects.create(number=2, semester=self.semester1, solutions_visible=True,
                                           start_time=start2, end_time=end2, visible=True)
        self.round3 = Round.objects.create(number=2, semester=self.semester2, solutions_visible=True,
                                           start_time=start3, end_time=end3, visible=True)
        self.task1 = Task.objects.create(number=1, name='Test task 1', round=self.round1)
        self.task2 = Task.objects.create(number=1, name='Test task 2', round=self.round2)
        self.task3 = Task.objects.create(number=1, name='Test task 3', round=self.round3)

        year = timezone.now().year + 2
        self.user = User.objects.create(username="TestUser", password="password",
                                        first_name="Jozko", last_name="Mrkvicka", graduation=year)
        self.url1 = reverse('view_results', kwargs={'round_id': self.round1.id})
        self.url2 = reverse('view_results', kwargs={'round_id': self.round2.id})
        self.url3 = reverse('view_results', kwargs={'round_id': self.round3.id})

    def test_invalid_round(self):
        url = reverse('view_results', kwargs={'round_id': get_noexisting_id(Round)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_one_round_no_users(self):
        response = self.client.get(self.url1)
        # @ToDo: translations
        self.assertContains(response, 'Žiadne submity')

    def test_submit_only_first_round(self):
        submit_time = self.round1.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task1, user=self.user, submit_type=0, points=5)
        submit.time = submit_time
        submit.save()
        response = self.client.get(self.url1)
        self.assertContains(response, self.user.get_full_name())
        response = self.client.get(self.url2)
        self.assertContains(response, self.user.get_full_name())
        response = self.client.get(self.url3)
        self.assertNotContains(response, self.user.get_full_name())

    def test_submit_only_second_round(self):
        submit_time = self.round2.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task2, user=self.user, submit_type=0, points=5)
        submit.time = submit_time
        submit.save()
        response = self.client.get(self.url1)
        self.assertNotContains(response, self.user.get_full_name())
        response = self.client.get(self.url2)
        self.assertContains(response, self.user.get_full_name())
        response = self.client.get(self.url3)
        self.assertNotContains(response, self.user.get_full_name())

    def test_submit_all(self):
        submit_time = self.round1.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task1, user=self.user, submit_type=0, points=5)
        submit.time = submit_time
        submit.save()

        submit_time = self.round2.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task2, user=self.user, submit_type=0, points=5)
        submit.time = submit_time
        submit.save()

        submit_time = self.round3.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task3, user=self.user, submit_type=0, points=5)
        submit.time = submit_time
        submit.save()

        response = self.client.get(self.url1)
        self.assertContains(response, self.user.get_full_name())
        response = self.client.get(self.url2)
        self.assertContains(response, self.user.get_full_name())
        response = self.client.get(self.url3)
        self.assertContains(response, self.user.get_full_name())

    def test_old_user(self):
        old_user = User.objects.create(username="TestOldUser", password="password",
                                       first_name="Jozko", last_name="Starcek", graduation=2010)
        submit = Submit.objects.create(task=self.task1, user=old_user, submit_type=0, points=5)
        submit.time = self.round1.start_time + timezone.timedelta(0, 5)
        submit.save()

        response = self.client.get(self.url1)
        self.assertNotContains(response, old_user.get_full_name())

        response = self.client.get("%s?show_staff=True" % self.url1)
        self.assertContains(response, old_user.get_full_name())

    def test_single_round(self):
        submit_time = self.round1.start_time + timezone.timedelta(0, 5)
        submit = Submit.objects.create(task=self.task1, user=self.user, submit_type=0, points=5)
        submit.time = submit_time
        submit.save()
        response = self.client.get("%s?single_round=True" % self.url2)
        self.assertNotContains(response, self.user.get_full_name())

        submit = Submit.objects.create(task=self.task2, user=self.user, submit_type=0, points=5)
        submit.time = self.round2.start_time + timezone.timedelta(0, 5)
        submit.save()
        response = self.client.get("%s?single_round=True" % self.url2)
        self.assertContains(response, self.user.get_full_name())
