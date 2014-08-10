# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from django.contrib.auth import get_user_model
from trojsten.regal.contests.models import Round, Competition
import os


class Category(models.Model):
    '''
    Competition consists of a few categories. Each task belongs to one or more
    categories.
    '''
    name = models.CharField(max_length=16, verbose_name='názov')
    competition = models.ForeignKey(Competition, verbose_name='súťaž')

    class Meta:
        verbose_name = 'Kategória'
        verbose_name_plural = 'Kategórie'

    def __str__(self):
        return str(self.competition.name) + '-' + str(self.name)


@python_2_unicode_compatible
class Task(models.Model):
    '''
    Task has its number, name, type and points value.
    Task has submits.
    '''
    name = models.CharField(max_length=128, verbose_name='názov')
    round = models.ForeignKey(Round, verbose_name='kolo')
    category = models.ManyToManyField(Category, verbose_name='kategória')
    number = models.IntegerField(verbose_name='číslo')
    description_points = models.IntegerField(verbose_name='body za popis')
    source_points = models.IntegerField(verbose_name='body za program')
    has_source = models.BooleanField(verbose_name='odovzáva sa zdroják')
    has_description = models.BooleanField(verbose_name='odovzáva sa popis')

    class Meta:
        verbose_name = 'Úloha'
        verbose_name_plural = 'Úlohy'

    def __str__(self):
        return str(self.number) + '. ' + str(self.name)

    def has_submit_type(self, submit_type):
        check_field = {
            Submit.SOURCE: self.has_source,
            Submit.DESCRIPTION: self.has_description,
        }
        return check_field[submit_type]


@python_2_unicode_compatible
class Submit(models.Model):
    '''
    Submit holds information about its task and person who submitted it.
    There are 2 types of submits. Description submit and source submit.
    Description submit has points and filename, Source submit has also
    tester response and protocol ID assigned.
    '''
    SOURCE = 0
    DESCRIPTION = 1
    SUBMIT_TYPES = [
        (SOURCE, 'source'),
        (DESCRIPTION, 'description'),
    ]
    task = models.ForeignKey(Task, verbose_name='úloha')
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), verbose_name='odovzdávateľ')
    submit_type = models.IntegerField(verbose_name='typ submitu', choices=SUBMIT_TYPES)
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
        return str(self.user) + ' - ' + str(self.task)

    def filename(self):
        return os.path.basename(self.filepath)
