# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from trojsten.regal.people.models import Person
from trojsten.regal.contests.models import Round
import os


@python_2_unicode_compatible
class SubmitType(models.Model):

    '''
    Any type of submit should be declared here and then linked to tasks
    with ManyToMany fields
    '''
    name = models.CharField(
        max_length=128, verbose_name='názov', primary_key=True)

    class Meta:
        verbose_name = 'Typ submitu'
        verbose_name_plural = 'Typy submitov'

    def __str__(self):
        return str(self.name)


@python_2_unicode_compatible
class Task(models.Model):

    '''
    Task has its number, name, type and points value.
    Task has submits.
    '''
    name = models.CharField(max_length=128, verbose_name='názov')
    round = models.ForeignKey(Round, verbose_name='Kolo')
    number = models.IntegerField(verbose_name='číslo')
    description_points = models.IntegerField(verbose_name='body za popis')
    source_points = models.IntegerField(verbose_name='body za program')
    task_types = models.ManyToManyField(SubmitType, verbose_name='typy úlohy')

    class Meta:
        verbose_name = 'Úloha'
        verbose_name_plural = 'Úlohy'

    def __str__(self):
        return str(self.number) + '. ' + str(self.name)


@python_2_unicode_compatible
class Submit(models.Model):

    '''
    Submit holds information about its task and person who submitted it.
    There are 2 types of submits. Description submit and source submit.
    Description submit has points and filename, Source submit has also
    tester response and protocol ID assigned.
    '''
    task = models.ForeignKey(Task, verbose_name='úloha')
    time = models.DateTimeField(auto_now_add=True)
    person = models.ForeignKey(Person, verbose_name='odovzdávateľ')
    submit_type = models.ForeignKey(SubmitType, verbose_name='typ submitu')
    points = models.IntegerField(verbose_name='body')
    filepath = models.CharField(max_length=128, verbose_name='súbor')
    testing_status = models.CharField(
        max_length=128, verbose_name='stav testovania')
    tester_response = models.CharField(
        max_length=10, verbose_name='odpoveď testovača')
    protocol_id = models.CharField(
        max_length=128, verbose_name='číslo protokolu')

    class Meta:
        verbose_name = 'Submit'
        verbose_name_plural = 'Submity'

    def __str__(self):
        return str(self.person) + ' - ' + str(self.task)

    def filename(self):
        return os.path.basename(self.filepath)
