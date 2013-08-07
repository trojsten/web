# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from django.db import models
from django.core.urlresolvers import reverse


class Competition(models.Model):

    '''
    Consists of years.
    '''
    name = models.CharField(max_length=128, verbose_name='názov')
    informatics = models.BooleanField(verbose_name='informatika')
    math = models.BooleanField(verbose_name='matematika')
    physics = models.BooleanField(verbose_name='fyzika')

    class Meta:
        verbose_name = 'Súťaž'
        verbose_name_plural = 'Súťaže'

    def __str__(self):
        return self.name


class Series(models.Model):

    '''
    Series consits of several rounds.
    '''
    competition = models.ForeignKey(Competition, verbose_name='súťaž')
    name = models.CharField(max_length=32, verbose_name='názov')
    start_date = models.DateField(verbose_name='dátum začiatk')
    year = models.IntegerField(verbose_name='ročník')

    class Meta:
        verbose_name = 'Séria'
        verbose_name_plural = 'Série'

    def __str__(self):
        return str(self.name)


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
