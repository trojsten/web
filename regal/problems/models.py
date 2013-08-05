# -*- coding: utf-8 -*- 
from django.db import models
from regal.contests.models import Round
from regal.people.models import Person

class Task(models.Model):
    '''
    '''
    in_round = models.ForeignKey(Round, verbose_name=u'kolo')
    name = models.CharField(max_length = 128,verbose_name=u'názov')
    number = models.IntegerField(verbose_name=u'#')

    class Meta:
        verbose_name = u'Príklad'
        verbose_name_plural = u'Príklady'

    def __unicode__(self):
        return self.name;

class Evaluation(models.Model):
    '''
    For storing points.
    '''
    task = models.ForeignKey(Task, verbose_name=u'úloha')
    person = models.ForeignKey(Person, verbose_name=u'riešiteľ')
    points = models.CharField(max_length = 10, verbose_name=u'body')
    submit = models.CharField(max_length = 128, verbose_name=u'submit')
    submit_type = models.CharField(max_length = 128, verbose_name=u'typ submitu')

    class Meta:
        verbose_name = u'Body za úlohu'
        verbose_name_plural = u'Body za úlohu'

    def __unicode__(self):
        return self.points
