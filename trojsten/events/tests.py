# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import Group

from trojsten.utils.test_utils import get_noexisting_id

from .models import Event, EventType, Invitation, Place, Registration
from wiki.models import Article, URLPath, ArticleRevision
from trojsten.people.models import User


class EventListTest(TestCase):

    def setUp(self):
        site = Site.objects.get(pk=settings.SITE_ID)

        article1 = Article.objects.create()
        urlpath1 = URLPath.objects.create(site=site, article=article1)
        ArticleRevision.objects.create(article=article1, title="Nazov1")

        article2 = Article.objects.create()
        urlpath2 = URLPath.objects.create(site=site, article=article2, slug="akcie",
                                          parent=urlpath1)
        ArticleRevision.objects.create(article=article2, title="Nazov1")

        article3 = Article.objects.create()
        URLPath.objects.create(site=site, article=article3, slug="sustredenia",
                               parent=urlpath2)
        ArticleRevision.objects.create(article=article3, title="Nazov1")

        self.url1 = reverse('event_list')
        self.url2 = reverse('camp_event_list')
        group = Group.objects.create(name="skupina")

        self.event_type1 = EventType.objects.create(name="nesustredenie",
                                                    organizers_group=group, is_camp=False)
        self.event_type2 = EventType.objects.create(name="sustredenie",
                                                    organizers_group=group, is_camp=True)
        self.event_type1.sites.add(site)
        self.event_type2.sites.add(site)

        self.place = Place.objects.create(name="Miesto")
        self.start_time = datetime.datetime.now()
        self.end_time = datetime.datetime.now() + datetime.timedelta(5)

    def test_no_event(self):
        response = self.client.get(self.url1)
        self.assertEqual(response.status_code, 200)

    def test_visible_event(self):
        event = Event.objects.create(name="Nesustredkovy event", type=self.event_type1,
                                     place=self.place, start_time=self.start_time,
                                     end_time=self.end_time)
        response = self.client.get(self.url1)
        self.assertContains(response, event.name)

    def test_event_is_not_camp(self):
        event = Event.objects.create(name="Nesustredkovy event", type=self.event_type1,
                                     place=self.place, start_time=self.start_time,
                                     end_time=self.end_time)
        response = self.client.get(self.url2)
        self.assertNotContains(response, event.name)

    def test_event_is_camp(self):
        event = Event.objects.create(name="Sustredkovy event", type=self.event_type2,
                                     place=self.place, start_time=self.start_time,
                                     end_time=self.end_time)
        response = self.client.get(self.url2)
        self.assertContains(response, event.name)


class EventTest(TestCase):

    def setUp(self):
        site = Site.objects.get(pk=settings.SITE_ID)

        article1 = Article.objects.create()
        urlpath1 = URLPath.objects.create(site=site, article=article1)
        ArticleRevision.objects.create(article=article1, title="Nazov1")

        article2 = Article.objects.create()
        URLPath.objects.create(site=site, article=article2, slug="akcie",
                               parent=urlpath1)
        ArticleRevision.objects.create(article=article2, title="Nazov1")

        group = Group.objects.create(name="skupina")

        self.event_type = EventType.objects.create(name="sustredenie",
                                                   organizers_group=group, is_camp=True)
        self.event_type.sites.add(site)

        self.place = Place.objects.create(name="Miesto")
        self.start_time = datetime.datetime.now()
        self.end_time = datetime.datetime.now() + datetime.timedelta(5)

    def test_invalid_event(self):
        url = reverse('event_detail', kwargs={'event_id': get_noexisting_id(Event)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_existing_event(self):
        event = Event.objects.create(name="Sustredkovy event", type=self.event_type,
                                     place=self.place, start_time=self.start_time,
                                     end_time=self.end_time)
        url = reverse('event_detail', kwargs={'event_id': event.id})
        response = self.client.get(url)
        self.assertContains(response, event.name)
        self.assertContains(response, event.place)


class EventParticipantsTest(TestCase):

    def setUp(self):
        site = Site.objects.get(pk=settings.SITE_ID)

        article1 = Article.objects.create()
        urlpath1 = URLPath.objects.create(site=site, article=article1)
        ArticleRevision.objects.create(article=article1, title="Nazov1")

        article2 = Article.objects.create()
        URLPath.objects.create(site=site, article=article2, slug="akcie",
                               parent=urlpath1)
        ArticleRevision.objects.create(article=article2, title="Nazov1")

        self.group = Group.objects.create(name="skupina")

        event_type = EventType.objects.create(name="sustredenie",
                                                   organizers_group=self.group, is_camp=True)
        event_type.sites.add(site)

        place = Place.objects.create(name="Miesto")
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now() + datetime.timedelta(5)

        self.event = Event.objects.create(name="Sustredkovy event", type=event_type,
                                          place=place, start_time=start_time,
                                          end_time=end_time)
        self.url = reverse('participants_list', kwargs={'event_id': self.event.id})

    def test_event_not_exists(self):
        url = reverse('participants_list', kwargs={'event_id': get_noexisting_id(Event)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_list_exists(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_event_has_participants(self):
        user = User.objects.create(username="jozko", first_name="Jozko", last_name="Mrkvicka",
                                   password="pass")
        Invitation.objects.create(event=self.event, user=user, going=True)
        response = self.client.get(self.url)
        self.assertContains(response, user.get_full_name())

    def test_participant_not_going(self):
        user = User.objects.create(username="jozko", first_name="Jozko", last_name="Mrkvicka",
                                   password="pass")
        Invitation.objects.create(event=self.event, user=user, going=False)
        response = self.client.get(self.url)
        self.assertNotContains(response, user.get_full_name())

    def test_event_has_staff(self):
        user = User.objects.create(username="jozko", first_name="Jozko", last_name="Mrkvicka",
                                   password="pass")
        self.group.user_set.add(user)
        Invitation.objects.create(event=self.event, user=user, going=True, type=2)
        response = self.client.get(self.url)
        self.assertContains(response, user.get_full_name())

    def test_participant_substitute_not_display(self):
        user = User.objects.create(username="jozko", first_name="Jozko", last_name="Mrkvicka",
                                   password="pass")
        Invitation.objects.create(event=self.event, user=user, going=True, type=1)
        response = self.client.get(self.url)
        self.assertNotContains(response, user.get_full_name())


class EventRegistrationTest(TestCase):

    def setUp(self):
        site = Site.objects.get(pk=settings.SITE_ID)
        self.group = Group.objects.create(name="skupina")

        event_type = EventType.objects.create(name="sustredenie",
                                                   organizers_group=self.group, is_camp=True)
        event_type.sites.add(site)

        place = Place.objects.create(name="Miesto")
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now() + datetime.timedelta(5)
        registration = Registration.objects.create(name="Registracia", text="")
        self.event = Event.objects.create(name="Sustredkovy event", type=event_type,
                                          place=place, start_time=start_time,
                                          end_time=end_time, registration=registration)

        article1 = Article.objects.create()
        urlpath1 = URLPath.objects.create(site=site, article=article1)
        ArticleRevision.objects.create(article=article1, title="Nazov1")

        article2 = Article.objects.create()
        URLPath.objects.create(site=site, article=article2, slug="akcie",
                               parent=urlpath1)
        ArticleRevision.objects.create(article=article2, title="Nazov1")

        self.user = User.objects.create_user(username="jozko", first_name="Jozko",
                                             last_name="Mrkvicka", password="pass")
        self.url = reverse('event_registration', kwargs={'event_id': self.event.id})

    def test_event_registration_redirect_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_event_registration_permission_denied(self):
        self.client.login(username='jozko', password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_registration_participant(self):
        self.client.login(username='jozko', password='pass')
        Invitation.objects.create(event=self.event, user=self.user, type=0)
        response = self.client.get(self.url)
        self.assertContains(response, self.event.name)
        # @ToDo: translations
        self.assertContains(response, "účastník")

    def test_registration_sub(self):
        self.client.login(username='jozko', password='pass')
        Invitation.objects.create(event=self.event, user=self.user, type=1)
        response = self.client.get(self.url)
        self.assertContains(response, self.event.name)
        # @ToDo: translations
        self.assertContains(response, "náhradník")

    def test_registration_staff(self):
        self.client.login(username='jozko', password='pass')
        Invitation.objects.create(event=self.event, user=self.user, type=2)
        response = self.client.get(self.url)
        self.assertContains(response, self.event.name)
        # @ToDo: translations
        self.assertContains(response, "vedúci")
