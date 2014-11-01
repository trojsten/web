# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model


@python_2_unicode_compatible
class EventType(models.Model):
    '''
    Type of event e.g. camp
    '''
    name = models.CharField(max_length=100, verbose_name='názov')
    sites = models.ManyToManyField(Site)
    organizers_group = models.ForeignKey(
        Group, verbose_name='skupina vedúcich'
    )

    class Meta:
        verbose_name = 'typ akcie'
        verbose_name_plural = 'typy akcií'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Link(models.Model):
    title = models.CharField(max_length=100, verbose_name='názov')
    url = models.URLField(max_length=300)

    class Meta:
        verbose_name = 'odkaz'
        verbose_name_plural = 'odkazy'

    def __str__(self):
        return '%s(%s)' % (self.title, self.url)


@python_2_unicode_compatible
class Place(models.Model):
    name = models.CharField(max_length=100, verbose_name='názov')
    address = models.ForeignKey('people.Address', null=True, blank=True)

    class Meta:
        verbose_name = 'miesto akcie'
        verbose_name_plural = 'miesta akcií'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Event(models.Model):
    name = models.CharField(max_length=100, verbose_name='názov')
    type = models.ForeignKey(EventType, verbose_name='typ akcie')
    place = models.ForeignKey(Place, verbose_name='miesto')
    start_time = models.DateTimeField(verbose_name='čas začiatku')
    end_time = models.DateTimeField(verbose_name='čas konca')
    links = models.ManyToManyField(
        Link, blank=True, verbose_name='zoznam odkazov'
    )

    @property
    def participants(self):
        return get_user_model().objects.invited_to(
            self, invitation_type=Invitation.PARTICIPANT, going_only=True
        )

    @property
    def organizers(self):
        return get_user_model().objects.invited_to(
            self, invitation_type=Invitation.ORGANIZER
        )

    class Meta:
        verbose_name = 'akcia'
        verbose_name_plural = 'akcie'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Invitation(models.Model):
    PARTICIPANT = 0
    RESERVE = 1
    ORGANIZER = 2
    TYPE_CHOICES = (
        (PARTICIPANT, 'účastník'),
        (RESERVE, 'náhradník'),
        (ORGANIZER, 'vedúci'),
    )
    event = models.ForeignKey(Event, verbose_name='akcia', related_name='invitations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='účastník')
    type = models.SmallIntegerField(
        choices=TYPE_CHOICES, default=PARTICIPANT, verbose_name='typ pozvánky'
    )
    going = models.NullBooleanField(verbose_name='zúčastní sa')

    class Meta:
        verbose_name = 'pozvánka'
        verbose_name_plural = 'pozvánky'
        unique_together = ('event', 'user')

    def __str__(self):
        return '%s(%s): %s (%s)' % (
            self.event, self.get_type_display(), self.user, self.going
        )
