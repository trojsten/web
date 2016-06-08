# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from trojsten.contests.models import Competition, Round
from trojsten.submit import constants as submit_constants


class TaskManager(models.Manager):
    def for_rounds_and_category(self, rounds, category=None):
        """Returns tasks which belong to specified rounds and category
        """
        if not rounds:
            return self.none()
        tasks = self.filter(
            round__in=rounds
        )
        if category is not None:
            tasks = tasks.filter(
                category=category
            )
        return tasks.order_by('round', 'number')


@python_2_unicode_compatible
class Category(models.Model):
    """
    Competition consists of a few categories. Each task belongs to one or more
    categories.
    """
    name = models.CharField(max_length=16, verbose_name='názov')
    competition = models.ForeignKey(Competition, verbose_name='súťaž')

    @property
    def full_name(self):
        return '%s-%s' % (self.competition.name, self.name)

    class Meta:
        verbose_name = 'Kategória'
        verbose_name_plural = 'Kategórie'

    def __str__(self):
        return self.full_name


@python_2_unicode_compatible
class Task(models.Model):
    """
    Task has its number, name, type and points value.
    Task has submits.
    """
    name = models.CharField(max_length=128, verbose_name='názov')
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        verbose_name='opravovateľ',
    )
    round = models.ForeignKey(Round, verbose_name='kolo')
    category = models.ManyToManyField(Category, verbose_name='kategória', blank=True)
    number = models.IntegerField(verbose_name='číslo')
    description_points = models.IntegerField(verbose_name='body za popis', default=0)
    source_points = models.IntegerField(verbose_name='body za program', default=0)
    integer_source_points = models.BooleanField(
        default=True, verbose_name='celočíselné body za program'
    )
    has_source = models.BooleanField(verbose_name='odovzdáva sa zdroják', default=False)
    has_description = models.BooleanField(verbose_name='odovzdáva sa popis', default=False)
    has_testablezip = models.BooleanField(
        verbose_name='odovzdáva sa zip na testovač', default=False
    )
    external_submit_link = models.CharField(
        max_length=128, verbose_name='Odkaz na externé odovzdávanie',
        blank=True, null=True,
    )

    objects = TaskManager()

    class Meta:
        verbose_name = 'Úloha'
        verbose_name_plural = 'Úlohy'

    def __str__(self):
        return '%i. %s, %s' % (self.number, self.name, self.round)

    def has_submit_type(self, submit_type):
        check_field = {
            submit_constants.SUBMIT_TYPE_SOURCE: self.has_source,
            submit_constants.SUBMIT_TYPE_DESCRIPTION: self.has_description,
            submit_constants.SUBMIT_TYPE_TESTABLE_ZIP: self.has_testablezip,
            submit_constants.SUBMIT_TYPE_EXTERNAL: bool(self.external_submit_link),
        }
        return check_field[submit_type]

    @property
    def has_submit_list(self):
        submit_list_types = set(st for st, _ in submit_constants.SUBMIT_TYPES) - {submit_constants.SUBMIT_TYPE_EXTERNAL}
        return bool(submit_list_types & set(self.get_submit_types()))

    def get_submit_types(self):
        return [
            submit_type
            for submit_type, _ in submit_constants.SUBMIT_TYPES
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
        return path

    def get_absolute_url(self):
        return reverse('solution_statement', kwargs={'task_id': self.id})

    @property
    def task_file_exists(self):
        path = self.get_path(solution=False)
        return os.path.exists(path)

    @property
    def solution_file_exists(self):
        path = self.get_path(solution=True)
        return os.path.exists(path)

    def visible(self, user):
        return self.round.is_visible_for_user(user)

    def solution_visible(self, user):
        return self.round.solutions_are_visible_for_user(user)
