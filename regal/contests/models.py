# -*- coding: utf-8 -*- 
from django.db import models
from datetime import datetime

class Competition(models.Model):
    """ Contest consists of years.
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

class Year(models.Model):
    """ Year consits of several rounds.
    """
    competition = models.ForeignKey(Competition,verbose_name=u'súťaž')
    number = models.IntegerField(verbose_name=u'číslo')
    year = models.IntegerField(verbose_name=u'rok')

    class Meta:
        verbose_name = u'Ročník'
        verbose_name_plural = u'Ročníky'

    def __unicode__(self):
        return str(self.number)+u'. ročník '+self.competition.__unicode__()

class Round(models.Model):
    """ Round has tasks.
        Holds informations about deadline and such things
    """
    year = models.ForeignKey(Year,verbose_name=u'ročník')
    number = models.IntegerField(verbose_name=u'číslo')
    end_time = models.DateTimeField(verbose_name=u'koniec')
    visible = models.BooleanField(verbose_name=u'viditeľnosť')

    class Meta:
        verbose_name = u'Kolo'
        verbose_name_plural = u'Kolá'

    def __unicode__(self):
        return str(self.number)+'. kolo'

class Task(models.Model):
    '''
    '''
    in_round = models.ForeignKey(Round, verbose_name=u'kolo')
    name = models.CharField(max_length = 128,verbose_name=u'názov')
    number = models.IntegerField(verbose_name=u'číslo')

    class Meta:
        verbose_name = u'Príklad'
        verbose_name_plural = u'Príklady'

    def __unicode__(self):
        return self.name;
