# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from ..people.models import Address


@python_2_unicode_compatible
class EventType(models.Model):
    '''
    Type of event e.g. camp
    '''
    name = models.CharField(max_length=100, verbose_name='názov')
    sites = models.ManyToManyField(Site)
    organizers_group = models.ForeignKey(
        Group, null=True, verbose_name='skupina vedúcich'
    )

    class Meta:
        verbose_name = 'Typ akcie'
        verbose_name_plural = 'Typy akcií'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class EventLink(models.Model):
    title = models.CharField(max_length=100, verbose_name='názov')
    url = models.URLField(max_length=300)

    class Meta:
        verbose_name = 'Odkaz'
        verbose_name_plural = 'Odkazy'

    def __str__(self):
        return '%s(%s)' % (self.title, self.url)


@python_2_unicode_compatible
class EventPlace(models.Model):
    name = models.CharField(max_length=100, verbose_name='názov')
    address = models.ForeignKey(Address, null=True, blank=True)

    class Meta:
        verbose_name = 'Miesto akcie'
        verbose_name_plural = 'Miesto akcie'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Event(models.Model):
    name = models.CharField(max_length=100, verbose_name='názov')
    event_type = models.ForeignKey(EventType, verbose_name='typ akcie')
    organizers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, verbose_name='zoznam vedúcich',
        blank=True, related_name='organizing_event_set',
    )
    place = models.ForeignKey(EventPlace, verbose_name='miesto')
    start_time = models.DateTimeField(verbose_name='čas začiatku')
    end_time = models.DateTimeField(verbose_name='čas konca')
    links = models.ManyToManyField(
        EventLink, blank=True, verbose_name='zoznam odkazov'
    )

    @property
    def participants(self):
        return get_user_model().objects.filter(
            eventinvitation__event=self, eventinvitation__type=EventInvitation.PARTICIPANT
        )

    class Meta:
        verbose_name = 'Akcie'
        verbose_name_plural = 'Akcie'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class EventInvitation(models.Model):
    PARTICIPANT = 0
    RESERVE = 1
    TYPE_CHOICES = (
        (PARTICIPANT, 'účastník'),
        (RESERVE, 'náhradník'),
    )
    event = models.ForeignKey(Event, verbose_name='akcia', related_name='invitations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='účastník')
    type = models.SmallIntegerField(
        choices=TYPE_CHOICES, default=PARTICIPANT, verbose_name='typ pozvánky'
    )
    going = models.NullBooleanField(verbose_name='zúčastní sa')

    class Meta:
        verbose_name = 'Pozvánka'
        verbose_name_plural = 'Pozvánky'

    def __str__(self):
        return '%s(%s): %s (%s)' % (
            self.event, self.invitation_type, self.user, self.going
        )
