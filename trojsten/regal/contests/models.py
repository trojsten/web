# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.sites.models import Site
import django.utils.timezone


@python_2_unicode_compatible
class Competition(models.Model):

    '''
    Consists of series.
    '''
    name = models.CharField(max_length=128, verbose_name='názov')
    sites = models.ManyToManyField(Site)

    class Meta:
        verbose_name = 'Súťaž'
        verbose_name_plural = 'Súťaže'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Series(models.Model):

    '''
    Series consits of several rounds.
    '''
    competition = models.ForeignKey(Competition, verbose_name='súťaž')
    name = models.CharField(max_length=32, verbose_name='názov')
    number = models.IntegerField(verbose_name='číslo série')
    year = models.IntegerField(verbose_name='ročník')

    class Meta:
        verbose_name = 'Séria'
        verbose_name_plural = 'Série'

    def __str__(self):
        return str(self.name)


@python_2_unicode_compatible
class Round(models.Model):

    '''
    Round has tasks.
    Holds information about deadline and such things
    '''
    series = models.ForeignKey(Series, verbose_name='séria')
    number = models.IntegerField(verbose_name='číslo')
    end_time = models.DateTimeField(verbose_name='koniec')
    visible = models.BooleanField(verbose_name='viditeľnosť')

    class Meta:
        verbose_name = 'Kolo'
        verbose_name_plural = 'Kolá'

    def __str__(self):
        return str(self.number) + '. kolo'
