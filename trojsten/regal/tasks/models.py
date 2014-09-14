# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from trojsten.regal.contests.models import Round, Competition
from django.utils.translation import ugettext_lazy as _
import os


@python_2_unicode_compatible
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
        return self.competition.name + '-' + self.name


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
    has_testablezip = models.BooleanField(verbose_name='odovzdáva sa zip na testovač', default=False)

    class Meta:
        verbose_name = 'Úloha'
        verbose_name_plural = 'Úlohy'

    def __str__(self):
        return '%i. %s, %s' % (self.number, self.name, self.round)

    def has_submit_type(self, submit_type):
        check_field = {
            Submit.SOURCE: self.has_source,
            Submit.DESCRIPTION: self.has_description,
            Submit.TESTABLE_ZIP: self.has_testablezip,
        }
        return check_field[submit_type]

    def get_submit_types(self):
        return [
            submit_type
            for submit_type, _ in Submit.SUBMIT_TYPES
            if self.has_submit_type(submit_type)
        ]

    def get_path(self, solution=False):
        task_file = '{}{}.html'.format(
            settings.TASK_STATEMENTS_PREFIX_TASK,
            self.number,
        )
        path = os.path.join(
            self.round.get_path(solution),
            settings.TASK_STATEMENTS_HTML_DIR,
            task_file,
        )
        if not os.path.exists(path):
            raise IOError("path '%s' doesn't exist" % path)
        return path

    @property
    def task_file_exists(self):
        try:
            self.get_path(solution=False)
            return True
        except IOError:
            return False

    @property
    def solution_file_exists(self):
        try:
            self.get_path(solution=True)
            return True
        except IOError:
            return False

    def visible(self, user):
        return user.is_superuser\
            or self.round.series.competition.organizers_group in user.groups.all()\
            or self.round.visible

    def solutions_visible(self, user):
        return user.is_superuser\
            or self.round.series.competition.organizers_group in user.groups.all()\
            or self.round.solutions_visible


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
    TESTABLE_ZIP = 2
    SUBMIT_TYPES = [
        (SOURCE, 'source'),
        (DESCRIPTION, 'description'),
        (TESTABLE_ZIP, 'testable_zip'),
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
        return '%s - %s <%s> (%s)' % (self.user, self.task, Submit.SUBMIT_TYPES[self.submit_type][1], str(self.time))

    @property
    def filename(self):
        return os.path.basename(self.filepath)

    @property
    def tester_response_verbose(self):
        return _(self.tester_response)
