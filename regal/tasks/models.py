# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from regal.people.models import Person


@python_2_unicode_compatible
class Task(models.Model):

    '''
    Task has its number and name.
    Task has submits.
    '''
    name = models.CharField(max_length=128, verbose_name='názov')
    number = models.IntegerField(verbose_name='číslo')

    class Meta:
        verbose_name = 'Úloha'
        verbose_name_plural = 'Úlohy'

    def __str__(self):
        return str(self.number) + '. ' + str(self.name)


@python_2_unicode_compatible
class Submit(models.Model):

    '''
    Submit holds information about its task and person who submitted it.
    Some submits also have responses from testers (especially tasks in
    informatics competitions)
    '''
    task = models.ForeignKey(Task, verbose_name='úloha')
    person = models.ForeignKey(Person, verbose_name='odovzdávateľ')
    desc_points = models.IntegerField(verbose_name='body za popis')
    source_points = models.IntegerField(verbose_name='body za zdroják')
    desc_filename = models.CharField(
        max_length=128, verbose_name='súbor s popisom')
    source_filename = models.CharField(
        max_length=128, verbose_name='súbor so zdrojákom')

    class Meta:
        verbose_name = 'Submit'
        verbose_name_plural = 'Submity'

    def __str__(self):
        return str(self.person) + ' - ' + str(self.task)
