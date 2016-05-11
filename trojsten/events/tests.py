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

        root_article = Article.objects.create()
        root_path = URLPath.objects.create(site=site, article=root_article)
        ArticleRevision.objects.create(article=root_article, title="Root article")

        events_article = Article.objects.create()
        events_path = URLPath.objects.create(site=site, article=events_article, slug="akcie",
                                             parent=root_path)
        ArticleRevision.objects.create(article=events_article, title="Events")

        camps_article = Article.objects.create()
        URLPath.objects.create(site=site, article=camps_article, slug="sustredenia",
                               parent=events_path)
        ArticleRevision.objects.create(article=camps_article, title="Camps")

        self.events_url = reverse('event_list')
        self.camp_url = reverse('camp_event_list')
        group = Group.objects.create(name="skupina")

        self.type_not_camp = EventType.objects.create(name="Not camp",
                                                      organizers_group=group, is_camp=False)
        self.type_camp = EventType.objects.create(name="Camp",
                                                  organizers_group=group, is_camp=True)
        self.type_not_camp.sites.add(site)
        self.type_camp.sites.add(site)

        self.place = Place.objects.create(name="Camp place")
        self.start_time = datetime.datetime.now()
        self.end_time = datetime.datetime.now() + datetime.timedelta(5)

    def test_no_event(self):
        response = self.client.get(self.events_url)
        # @ToDo: translations
        self.assertContains(response, "Žiadne akcie")

    def test_visible_event(self):
        not_camp_event = Event.objects.create(name="Not camp event", type=self.type_not_camp,
                                              place=self.place, start_time=self.start_time,
                                              end_time=self.end_time)
        response = self.client.get(self.events_url)
        self.assertContains(response, not_camp_event.name)

    def test_event_is_not_camp(self):
        not_camp_event = Event.objects.create(name="Not camp event", type=self.type_not_camp,
                                              place=self.place, start_time=self.start_time,
                                              end_time=self.end_time)
        response = self.client.get(self.camp_url)
        self.assertNotContains(response, not_camp_event.name)

    def test_event_is_camp(self):
        camp_event = Event.objects.create(name="Camp event", type=self.type_camp,
                                          place=self.place, start_time=self.start_time,
                                          end_time=self.end_time)
        response = self.client.get(self.camp_url)
        self.assertContains(response, camp_event.name)


class EventTest(TestCase):

    def setUp(self):
        site = Site.objects.get(pk=settings.SITE_ID)

        root_article = Article.objects.create()
        root_path = URLPath.objects.create(site=site, article=root_article)
        ArticleRevision.objects.create(article=root_article, title="Root article")

        events_article = Article.objects.create()
        URLPath.objects.create(site=site, article=events_article, slug="akcie",
                               parent=root_path)
        ArticleRevision.objects.create(article=events_article, title="Events")

        group = Group.objects.create(name="group")

        self.type_camp = EventType.objects.create(name="Camp",
                                                  organizers_group=group, is_camp=True)
        self.type_camp.sites.add(site)

        self.place = Place.objects.create(name="Camp place")
        self.start_time = datetime.datetime.now()
        self.end_time = datetime.datetime.now() + datetime.timedelta(5)
        self.grad_year = datetime.datetime.now().year

    def test_invalid_event(self):
        url = reverse('event_detail', kwargs={'event_id': get_noexisting_id(Event)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_existing_event(self):
        event = Event.objects.create(name="Camp event", type=self.type_camp,
                                     place=self.place, start_time=self.start_time,
                                     end_time=self.end_time)
        url = reverse('event_detail', kwargs={'event_id': event.id})
        response = self.client.get(url)
        self.assertContains(response, event.name)
        self.assertContains(response, event.place)
        # @ToDo: translations
        self.assertContains(response, "Zoznam účastníkov")

    def test_visible_application(self):
        registration = Registration.objects.create(name="Registracia", text="")
        event = Event.objects.create(name="Camp event", type=self.type_camp,
                                     place=self.place, start_time=self.start_time,
                                     end_time=self.end_time, registration=registration)
        user_invited = User.objects.create_user(username="invited",
                                                graduation=self.grad_year)
        user_not_invited = User.objects.create_user(username="notinvited",
                                                    graduation=self.grad_year)
        Invitation.objects.create(event=event, user=user_invited, type=0)
        url = reverse('event_detail', kwargs={'event_id': event.id})
        self.client.force_login(user_invited)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Prihláška")
        self.client.force_login(user_not_invited)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertNotContains(response, "Prihláška")

    def test_visible_applic_for_sub(self):
        registration = Registration.objects.create(name="Registracia", text="")
        event = Event.objects.create(name="Camp event", type=self.type_camp,
                                     place=self.place, start_time=self.start_time,
                                     end_time=self.end_time, registration=registration)
        sub_invited = User.objects.create_user(username="invited",
                                               graduation=self.grad_year)
        Invitation.objects.create(event=event, user=sub_invited, type=1)
        url = reverse('event_detail', kwargs={'event_id': event.id})
        self.client.force_login(sub_invited)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Prihláška")

    def test_visible_applic_for_staff(self):
        registration = Registration.objects.create(name="Registracia", text="")
        event = Event.objects.create(name="Camp event", type=self.type_camp,
                                     place=self.place, start_time=self.start_time,
                                     end_time=self.end_time, registration=registration)
        staff_invited = User.objects.create_user(username="invited",
                                                 graduation=self.grad_year)
        Invitation.objects.create(event=event, user=staff_invited, type=2)
        url = reverse('event_detail', kwargs={'event_id': event.id})
        self.client.force_login(staff_invited)
        response = self.client.get(url)
        # @ToDo: translations
        self.assertContains(response, "Prihláška")


class EventParticipantsTest(TestCase):

    def setUp(self):
        site = Site.objects.get(pk=settings.SITE_ID)

        root_article = Article.objects.create()
        root_path = URLPath.objects.create(site=site, article=root_article)
        ArticleRevision.objects.create(article=root_article, title="Nazov1")

        events_article = Article.objects.create()
        URLPath.objects.create(site=site, article=events_article, slug="akcie",
                               parent=root_path)
        ArticleRevision.objects.create(article=events_article, title="Nazov1")

        self.group = Group.objects.create(name="skupina")

        type_camp = EventType.objects.create(name="sustredenie",
                                             organizers_group=self.group, is_camp=True)
        type_camp.sites.add(site)

        place = Place.objects.create(name="Miesto")
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now() + datetime.timedelta(5)

        self.event = Event.objects.create(name="Sustredkovy event", type=type_camp,
                                          place=place, start_time=start_time,
                                          end_time=end_time)
        self.part_list_url = reverse('participants_list', kwargs={'event_id': self.event.id})
        self.grad_year = datetime.datetime.now().year

    def test_event_not_exists(self):
        url = reverse('participants_list', kwargs={'event_id': get_noexisting_id(Event)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_event_has_participants(self):
        user = User.objects.create(username="jozko", first_name="Jozko", last_name="Mrkvicka",
                                   password="pass", graduation=self.grad_year)
        Invitation.objects.create(event=self.event, user=user, going=True)
        response = self.client.get(self.part_list_url)
        self.assertContains(response, user.get_full_name())

    def test_participant_not_going(self):
        user = User.objects.create(username="jozko", first_name="Jozko", last_name="Mrkvicka",
                                   password="pass", graduation=self.grad_year)
        Invitation.objects.create(event=self.event, user=user, going=False)
        response = self.client.get(self.part_list_url)
        self.assertNotContains(response, user.get_full_name())

    def test_event_has_staff(self):
        staff_user = User.objects.create(username="jozko", first_name="Jozko", last_name="Mrkvicka",
                                         password="pass", graduation=2000)
        self.group.user_set.add(staff_user)
        Invitation.objects.create(event=self.event, user=staff_user, going=True, type=2)
        response = self.client.get(self.part_list_url)
        self.assertContains(response, staff_user.get_full_name())

    def test_participant_substitute_not_display(self):
        user = User.objects.create(username="jozko", first_name="Jozko", last_name="Mrkvicka",
                                   password="pass", graduation=self.grad_year)
        Invitation.objects.create(event=self.event, user=user, going=True, type=1)
        response = self.client.get(self.part_list_url)
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

        root_article = Article.objects.create()
        root_path = URLPath.objects.create(site=site, article=root_article)
        ArticleRevision.objects.create(article=root_article, title="Nazov1")

        events_article = Article.objects.create()
        URLPath.objects.create(site=site, article=events_article, slug="akcie",
                               parent=root_path)
        ArticleRevision.objects.create(article=events_article, title="Nazov1")

        grad_year = datetime.datetime.now().year
        self.user = User.objects.create_user(username="jozko", first_name="Jozko",
                                             last_name="Mrkvicka", password="pass",
                                             graduation=grad_year)
        self.event_reg_url = reverse('event_registration', kwargs={'event_id': self.event.id})

    def test_event_registration_redirect_to_login(self):
        response = self.client.get(self.event_reg_url)
        self.assertEqual(response.status_code, 302)

    def test_event_registration_permission_denied(self):
        self.client.force_login(self.user)
        response = self.client.get(self.event_reg_url)
        self.assertEqual(response.status_code, 403)

    def test_registration_participant(self):
        Invitation.objects.create(event=self.event, user=self.user, type=0)
        self.client.force_login(self.user)
        response = self.client.get(self.event_reg_url)
        self.assertContains(response, self.event.name)
        # @ToDo: translations
        self.assertContains(response, "účastník")

    def test_registration_sub(self):
        Invitation.objects.create(event=self.event, user=self.user, type=1)
        self.client.force_login(self.user)
        response = self.client.get(self.event_reg_url)
        self.assertContains(response, self.event.name)
        # @ToDo: translations
        self.assertContains(response, "náhradník")

    def test_registration_staff(self):
        Invitation.objects.create(event=self.event, user=self.user, type=2)
        self.client.force_login(self.user)
        response = self.client.get(self.event_reg_url)
        self.assertContains(response, self.event.name)
        # @ToDo: translations
        self.assertContains(response, "vedúci")
