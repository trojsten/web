# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model


@python_2_unicode_compatible
class EventType(models.Model):
    '''
    Type of event e.g. campus
    '''
    name = models.CharField(max_length=100, verbose_name='názov')
    sites = models.ManyToManyField(Site)
    organizers_group = models.ForeignKey(Group, null=True, verbose_name='skupina vedúcich')

    class Meta:
        verbose_name = 'Typ akcie'
        verbose_name_plural = 'Typy akcií'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class EventLink(models.Model):
    title = models.CharField(max_length=100, verbose_name='názov')
    url = models.CharField(max_length=300)

    class Meta:
        verbose_name = 'Odkaz'
        verbose_name_plural = 'Odkazy'

    def __str__(self):
        return '%s(%s)' % (self.title, self.url)


@python_2_unicode_compatible
class EventPlace(models.Model):
    name = models.CharField(max_length=100, verbose_name='názov')

    class Meta:
        verbose_name = 'Miesto akcie'
        verbose_name_plural = 'Miesto akcie'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Event(models.Model):
    name = models.CharField(max_length=100, verbose_name='názov')
    event_type = models.ForeignKey(EventType, verbose_name='typ akcie')
    list_of_organizers = models.ManyToManyField(get_user_model(), verbose_name='zoznam vedúcich', blank=True, related_name='organizing_event_set')
    list_of_participants = models.ManyToManyField(get_user_model(), verbose_name='zoznam účastníkov', blank=True, related_name='participating_event_set')
    place = models.ForeignKey(EventPlace, verbose_name='miesto')
    start_time = models.DateTimeField(verbose_name='čas začiatku')
    end_time = models.DateTimeField(verbose_name='čas konca')
    links = models.ManyToManyField(EventLink, blank=True, verbose_name='zoznam odkazov')

    class Meta:
        verbose_name = 'Akcie'
        verbose_name_plural = 'Akcie'

    def __str__(self):
        return self.name
