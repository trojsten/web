# -*- coding: utf-8 -*-

import binascii
import os
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from markdown import markdown

from trojsten.contests.models import Task
from trojsten.people.constants import GRADUATION_SCHOOL_YEAR, SCHOOL_YEAR_END_MONTH
from trojsten.people.models import User
from trojsten.submit import constants as submit_constants


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
            if tasks[0].round.semester.competition.primary_school_only:
                minimal_year_of_graduation += GRADUATION_SCHOOL_YEAR
            submits = submits.exclude(user__graduation__lt=minimal_year_of_graduation).exclude(
                user__in=User.objects.filter(
                    groups=tasks[0].round.semester.competition.organizers_group
                )
            )

        return (
            submits.filter(task__in=tasks)
            .filter(
                models.Q(time__lte=models.F("task__round__end_time"))
                | models.Q(testing_status=submit_constants.SUBMIT_STATUS_REVIEWED)
            )
            .order_by("user", "task", "submit_type", "-time", "-id")
            .distinct("user", "task", "submit_type")
            .select_related("user__school", "task")
        )

    # @FIXME: This is used for rendering points for each task at task_list view.
    #  Displaying scores for tasks should be implemented in results/rules.
    def latest_for_user(self, tasks, user):
        """Returns latest submits which belong to specified tasks and user.
        Only one submit per submit type and task is returned.
        """
        return (
            self.filter(user=user, task__in=tasks)
            .filter(
                (
                    models.Q(task__round__second_end_time__isnull=False)
                    & models.Q(submit_type=submit_constants.SUBMIT_TYPE_SOURCE)
                    & models.Q(time__lte=models.F("task__round__second_end_time"))
                )
                | models.Q(time__lte=models.F("task__round__end_time"))
                | models.Q(testing_status=submit_constants.SUBMIT_STATUS_REVIEWED)
            )
            .order_by("task", "submit_type", "-time", "-id")
            .distinct("task", "submit_type")
        )


class Submit(models.Model):
    """
    Submit holds information about its task and person who submitted it.
    There are 2 types of submits. Description submit and source submit.
    Description submit has points and filename, Source submit has also
    tester response and protocol ID assigned.
    """

    task = models.ForeignKey(Task, verbose_name="úloha", on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now, verbose_name="čas")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="odovzdávateľ", on_delete=models.CASCADE
    )
    submit_type = models.IntegerField(
        verbose_name="typ submitu", choices=submit_constants.SUBMIT_TYPES
    )
    points = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="body")

    filepath = models.CharField(max_length=512, verbose_name="súbor", blank=True)
    testing_status = models.CharField(
        max_length=128,
        verbose_name="stav testovania",
        blank=True,
        choices=submit_constants.SUBMIT_STATUS_CHOICES,
    )
    tester_response = models.CharField(
        max_length=10,
        verbose_name="odpoveď testovača",
        blank=True,
        help_text="Očakávané odpovede sú %s"
        % (", ".join(submit_constants.SUBMIT_VERBOSE_RESPONSE.keys()),),
    )
    protocol_id = models.CharField(
        db_index=True, max_length=128, verbose_name="číslo protokolu", blank=True
    )

    reviewer_comment = models.TextField(verbose_name="komentár od opravovateľa", blank=True)
    protocol = models.TextField(verbose_name="protokol", blank=True, null=True)

    objects = SubmitManager()

    class Meta:
        verbose_name = "Submit"
        verbose_name_plural = "Submity"

    def __str__(self):
        return "%s - %s <%s> (%s)" % (
            self.user,
            self.task,
            submit_constants.SUBMIT_TYPES[self.submit_type][1],
            str(self.time),
        )

    def __init__(self, *args, **kwargs):
        super(Submit, self).__init__(*args, **kwargs)
        self.previous_points = self.points

    def save(self, *args, **kwargs):
        super(Submit, self).save(*args, **kwargs)
        self.previous_points = self.points

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
            return value.quantize(Decimal("1.00"))

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
            self.submit_type == submit_constants.SUBMIT_TYPE_DESCRIPTION
            or self.task.integer_source_points,
        )


class ExternalSubmitToken(models.Model):
    token = models.CharField(verbose_name="token", max_length=40, primary_key=True)
    name = models.CharField(verbose_name="názov", max_length=64)
    task = models.ForeignKey(Task, verbose_name="úloha", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super(ExternalSubmitToken, self).save(*args, **kwargs)

    def generate_token(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.name
