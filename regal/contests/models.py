# -*- coding: utf-8 -*- 
from django.db import models
from datetime import datetime
from django.core.urlresolvers import reverse

class Competition(models.Model):
    """
    Consists of years.
    """
    name = models.CharField(max_length = 128, verbose_name=u'názov')
    informatics = models.BooleanField(verbose_name=u'informatika')
    math = models.BooleanField(verbose_name=u'matematika')
    physics = models.BooleanField(verbose_name=u'fyzika')

    class Meta:
        verbose_name = u'Súťaž'
        verbose_name_plural = u'Súťaže'

    def __unicode__(self):
        return self.name

class Series(models.Model):
    """
    Series consits of several rounds.
    """
    competition = models.ForeignKey(Competition,verbose_name=u'súťaž')
    name = models.CharField(max_length = 32, verbose_name=u'názov')
    start_date = models.DateField(verbose_name=u'dátum začiatku')
    year = models.IntegerField(verbose_name=u'ročník')

    class Meta:
        verbose_name = u'Séria'
        verbose_name_plural = u'Série'

    def __unicode__(self):
        return str(self.name)

class Round(models.Model):
    """ 
    Round has tasks.
    Holds information about deadline and such things
    """
    series = models.ForeignKey(Series,verbose_name=u'séria')
    number = models.IntegerField(verbose_name=u'číslo')
    end_time = models.DateTimeField(verbose_name=u'koniec')
    visible = models.BooleanField(verbose_name=u'viditeľnosť')

    class Meta:
        verbose_name = u'Kolo'
        verbose_name_plural = u'Kolá'

    def __unicode__(self):
        return str(self.number)+'. kolo'
