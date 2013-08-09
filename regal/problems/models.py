# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from regal.contests.models import Round
from regal.people.models import Person


@python_2_unicode_compatible
class Task(models.Model):

    '''
    '''
    in_round = models.ForeignKey(Round, verbose_name='kolo')
    name = models.CharField(max_length=128, verbose_name='názov')
    number = models.IntegerField(verbose_name='#')

    class Meta:
        verbose_name = 'Príklad'
        verbose_name_plural = 'Príklady'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Evaluation(models.Model):

    '''
    For storing points.
    '''
    task = models.ForeignKey(Task, verbose_name='úloha')
    person = models.ForeignKey(Person, verbose_name='riešiteľ')
    points = models.CharField(max_length=10, verbose_name='body')
    submit = models.CharField(max_length=128, verbose_name='submit')
    submit_type = models.CharField(
        max_length=128, verbose_name='typ submit')

    class Meta:
        verbose_name = 'Body za úlohu'
        verbose_name_plural = 'Body za úlohy'

    def __str__(self):
        return self.points
