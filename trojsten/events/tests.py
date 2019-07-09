# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import pytz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from wiki.models import Article, ArticleRevision, URLPath

from trojsten.people.models import User
from trojsten.utils.test_utils import get_noexisting_id

from .models import Event, EventParticipant, EventPlace, EventType


class EventListTest(TestCase):
    def setUp(self):
        site = Site.objects.get(pk=settings.SITE_ID)

        root_article = Article.objects.create()
        root_path = URLPath.objects.create(site=site, article=root_article)
        ArticleRevision.objects.create(article=root_article, title="Root article")

        events_article = Article.objects.create()
        events_path = URLPath.objects.create(
            site=site, article=events_article, slug="akcie", parent=root_path
        )
        ArticleRevision.objects.create(article=events_article, title="Events")

        camps_article = Article.objects.create()
        URLPath.objects.create(
            site=site, article=camps_article, slug="sustredenia", parent=events_path
        )
        ArticleRevision.objects.create(article=camps_article, title="Camps")

        self.events_url = reverse("event_list")
        self.camp_url = reverse("camp_event_list")
        group = Group.objects.create(name="skupina")

        self.type_not_camp = EventType.objects.create(
            name="Not camp", organizers_group=group, is_camp=False
        )
        self.type_camp = EventType.objects.create(name="Camp", organizers_group=group, is_camp=True)
        self.type_not_camp.sites.add(site)
        self.type_camp.sites.add(site)

        self.place = EventPlace.objects.create(name="Camp place")
        self.start_time = timezone.now()
        self.end_time = timezone.now() + timezone.timedelta(5)

    def test_no_event(self):
        response = self.client.get(self.events_url)
        # @ToDo: translations
        self.assertContains(response, "Žiadne akcie")

    def test_visible_event(self):
        not_camp_event = Event.objects.create(
            name="Not camp event",
            type=self.type_not_camp,
            place=self.place,
            start_time=self.start_time,
            end_time=self.end_time,
        )
        response = self.client.get(self.events_url)
        self.assertContains(response, not_camp_event.name)

    def test_event_is_not_camp(self):
        not_camp_event = Event.objects.create(
            name="Not camp event",
            type=self.type_not_camp,
            place=self.place,
            start_time=self.start_time,
            end_time=self.end_time,
        )
        response = self.client.get(self.camp_url)
        self.assertNotContains(response, not_camp_event.name)

    def test_event_is_camp(self):
        camp_event = Event.objects.create(
            name="Camp event",
            type=self.type_camp,
            place=self.place,
            start_time=self.start_time,
            end_time=self.end_time,
        )
        response = self.client.get(self.camp_url)
        self.assertContains(response, camp_event.name)


class EventTest(TestCase):
    def setUp(self):
        site = Site.objects.get(pk=settings.SITE_ID)

        root_article = Article.objects.create()
        root_path = URLPath.objects.create(site=site, article=root_article)
        ArticleRevision.objects.create(article=root_article, title="Root article")

        events_article = Article.objects.create()
        URLPath.objects.create(site=site, article=events_article, slug="akcie", parent=root_path)
        ArticleRevision.objects.create(article=events_article, title="Events")

        group = Group.objects.create(name="group")

        self.type_camp = EventType.objects.create(name="Camp", organizers_group=group, is_camp=True)
        self.type_camp.sites.add(site)

        self.place = EventPlace.objects.create(name="Camp place")
        self.start_time = timezone.now()
        self.end_time = timezone.now() + timezone.timedelta(5)
        self.grad_year = timezone.now().year

    def test_invalid_event(self):
        url = reverse("event_detail", kwargs={"event_id": get_noexisting_id(Event)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_existing_event(self):
        event = Event.objects.create(
            name="Camp event",
            type=self.type_camp,
            place=self.place,
            start_time=self.start_time,
            end_time=self.end_time,
        )
        url = reverse("event_detail", kwargs={"event_id": event.id})
        response = self.client.get(url)
        self.assertContains(response, event.name)
        self.assertContains(response, event.place)
        # @ToDo: translations
        self.assertContains(response, "Zoznam účastníkov")


class EventParticipantsTest(TestCase):
    def setUp(self):
        site = Site.objects.get(pk=settings.SITE_ID)

        root_article = Article.objects.create()
        root_path = URLPath.objects.create(site=site, article=root_article)
        ArticleRevision.objects.create(article=root_article, title="Nazov1")

        events_article = Article.objects.create()
        URLPath.objects.create(site=site, article=events_article, slug="akcie", parent=root_path)
        ArticleRevision.objects.create(article=events_article, title="Nazov1")

        self.group = Group.objects.create(name="skupina")

        type_camp = EventType.objects.create(
            name="sustredenie", organizers_group=self.group, is_camp=True
        )
        type_camp.sites.add(site)

        place = EventPlace.objects.create(name="Miesto")
        start_time = timezone.now()
        end_time = timezone.now() + timezone.timedelta(5)

        self.event = Event.objects.create(
            name="Sustredkovy event",
            type=type_camp,
            place=place,
            start_time=start_time,
            end_time=end_time,
        )
        self.part_list_url = reverse("participants_list", kwargs={"event_id": self.event.id})
        self.grad_year = timezone.now().year

    def test_event_not_exists(self):
        url = reverse("participants_list", kwargs={"event_id": get_noexisting_id(Event)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_event_has_participants(self):
        user = User.objects.create(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=self.grad_year,
        )
        EventParticipant.objects.create(event=self.event, user=user, going=True)
        response = self.client.get(self.part_list_url)
        self.assertContains(response, user.get_full_name())

    def test_participant_not_going(self):
        user = User.objects.create(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=self.grad_year,
        )
        EventParticipant.objects.create(event=self.event, user=user, going=False)
        response = self.client.get(self.part_list_url)
        self.assertNotContains(response, user.get_full_name())

    def test_participant_substitute_not_going(self):
        user = User.objects.create(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=self.grad_year,
        )
        EventParticipant.objects.create(event=self.event, user=user, going=False, type=1)
        response = self.client.get(self.part_list_url)
        self.assertNotContains(response, user.get_full_name())

    def test_event_has_staff(self):
        staff_user = User.objects.create(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=2000,
        )
        self.group.user_set.add(staff_user)
        EventParticipant.objects.create(event=self.event, user=staff_user, going=True, type=2)
        response = self.client.get(self.part_list_url)
        self.assertContains(response, staff_user.get_full_name())

    def test_participant_substitute_display(self):
        user = User.objects.create(
            username="jozko",
            first_name="Jozko",
            last_name="Mrkvicka",
            password="pass",
            graduation=self.grad_year,
        )
        EventParticipant.objects.create(event=self.event, user=user, going=True, type=1)
        response = self.client.get(self.part_list_url)
        self.assertContains(response, user.get_full_name())


class ParticipantsAndOrganizersListViewTest(TestCase):
    def test_school_year(self):
        current_year = timezone.now().year
        site = Site.objects.get(pk=settings.SITE_ID)
        user = User.objects.create(
            username="ferko", first_name="Ferko", last_name="Mrkvicka", graduation=current_year - 1
        )
        group = Group.objects.create(name="skupina")
        place = EventPlace.objects.create(name="Miesto")
        type_camp = EventType.objects.create(
            name="sustredenie", organizers_group=group, is_camp=True
        )
        type_camp.sites.add(site)
        event = Event.objects.create(
            start_time=datetime.datetime(day=12, month=3, year=current_year - 2, tzinfo=pytz.utc),
            end_time=datetime.datetime(day=17, month=3, year=current_year - 2, tzinfo=pytz.utc),
            place=place,
            type=type_camp,
        )
        EventParticipant.objects.create(event=event, user=user, going=True, type=0)

        part_list_url = reverse("participants_list", kwargs={"event_id": event.id})
        response = self.client.get(part_list_url)

        self.assertContains(response, "<td>3</td>")
