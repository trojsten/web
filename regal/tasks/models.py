# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
import django.utils.timezone
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
    Some submits also have responses from testers (especially tasks in informatics competitions)
    '''
    task = models.ForeignKey(Task, verbose_name='úloha')
    person = models.ForeignKey(Person, verbose_name='odovzdávateľ')
    points = models.IntegerField(verbose_name='body')

    class Meta:
        verbose_name = 'Submit'
        verbose_name_plural = 'Submity'

    def __str__(self):
        return str(self.person) + ' - ' + str(self.task)
