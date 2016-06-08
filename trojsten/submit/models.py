# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.safestring import mark_safe
from markdown import markdown

from trojsten.people.constants import (GRADUATION_SCHOOL_YEAR,
                                       SCHOOL_YEAR_END_MONTH)
from trojsten.people.models import User
from trojsten.submit import constants as submit_constants
from trojsten.tasks.models import Task


class SubmitManager(models.Manager):
    # @FIXME(unused): Was used only by results, splitted to ResultsGenerator.
    def for_tasks(self, tasks, include_staff=False):
        """Returns submits which belong to specified tasks.
        Only one submit per user, submit type and task is returned.
        Submits made after round.end_time are not counted except review submits,
        which has testing_status=SUBMIT_STATUS_REVIEWED and are made by organizers.
        """
        submits = self
        if not include_staff and tasks:
            # round ends January 2014 => exclude 2013, 2012,
            # round ends Jun 2014 => exclude 2013, 2012,
            # round ends September 2014 => exclude 2014, 2013,
            # round ends December 2014 => exclude 2014, 2013,
            minimal_year_of_graduation = tasks[0].round.end_time.year + int(
                tasks[0].round.end_time.month > SCHOOL_YEAR_END_MONTH
            )
            if tasks[0].round.series.competition.primary_school_only:
                minimal_year_of_graduation += GRADUATION_SCHOOL_YEAR
            submits = submits.exclude(
                user__graduation__lt=minimal_year_of_graduation
            ).exclude(
                user__in=User.objects.filter(
                    groups=tasks[0].round.series.competition.organizers_group
                )
            )

        return submits.filter(
            task__in=tasks,
        ).filter(
            models.Q(time__lte=models.F('task__round__end_time')) |
            models.Q(testing_status=submit_constants.SUBMIT_STATUS_REVIEWED)
        ).order_by(
            'user', 'task', 'submit_type', '-time', '-id',
        ).distinct(
            'user', 'task', 'submit_type'
        ).select_related('user__school', 'task')

    def latest_for_user(self, tasks, user):
        """Returns latest submits which belong to specified tasks and user.
        Only one submit per submit type and task is returned.
        """
        return self.filter(
            user=user,
            task__in=tasks,
        ).filter(
            models.Q(time__lte=models.F('task__round__end_time')) |
            models.Q(testing_status=submit_constants.SUBMIT_STATUS_REVIEWED)
        ).order_by(
            'task', 'submit_type', '-time', '-id',
        ).distinct(
            'task', 'submit_type'
        )


@python_2_unicode_compatible
class Submit(models.Model):
    """
    Submit holds information about its task and person who submitted it.
    There are 2 types of submits. Description submit and source submit.
    Description submit has points and filename, Source submit has also
    tester response and protocol ID assigned.
    """
    task = models.ForeignKey(Task, verbose_name='úloha')
    time = models.DateTimeField(auto_now_add=True, verbose_name='čas')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='odovzdávateľ')
    submit_type = models.IntegerField(verbose_name='typ submitu', choices=submit_constants.SUBMIT_TYPES)
    points = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='body')

    filepath = models.CharField(max_length=128, verbose_name='súbor', blank=True)
    testing_status = models.CharField(
        max_length=128, verbose_name='stav testovania', blank=True)
    tester_response = models.CharField(
        max_length=10, verbose_name='odpoveď testovača', blank=True,
        help_text='Očakávané odpovede sú %s' % (
            ', '.join(submit_constants.SUBMIT_VERBOSE_RESPONSE.keys()),
        )
    )
    protocol_id = models.CharField(
        max_length=128, verbose_name='číslo protokolu', blank=True)

    reviewer_comment = models.TextField(verbose_name='komentár od opravovateľa', blank=True)

    objects = SubmitManager()

    class Meta:
        verbose_name = 'Submit'
        verbose_name_plural = 'Submity'

    def __str__(self):
        return '%s - %s <%s> (%s)' % (
            self.user,
            self.task,
            submit_constants.SUBMIT_TYPES[self.submit_type][1],
            str(self.time),
        )

    @property
    def protocol_path(self):
        return self.filepath.rsplit('.', 1)[0] + settings.PROTOCOL_FILE_EXTENSION

    @property
    def filename(self):
        return os.path.basename(self.filepath)

    @property
    def rendered_comment(self):
        return mark_safe(markdown(self.reviewer_comment, safe_mode=False))

    @property
    def tester_response_verbose(self):
        return submit_constants.SUBMIT_VERBOSE_RESPONSE.get(
            self.tester_response, self.tester_response
        )

    @staticmethod
    def display_decimal_value(value, is_integer):
        if is_integer:
            return value.quantize(Decimal(1))
        else:
            return value.quantize(Decimal('1.00'))

    @property
    def tested(self):
        return self.testing_status == submit_constants.SUBMIT_STATUS_FINISHED

    @property
    def user_points(self):
        """
        Returns points visible to user.
        Description points is always converted to integer.
        Source points are converted to integer if self.task.integer_source_points == True
        """
        return Submit.display_decimal_value(
            self.points,
            self.submit_type == submit_constants.SUBMIT_TYPE_DESCRIPTION or self.task.integer_source_points,
        )