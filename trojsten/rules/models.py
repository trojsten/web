# -*- coding: utf-8 -*-

from collections import defaultdict

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from trojsten.contests.models import Semester
from trojsten.events.models import Event


class KSPLevelManager(models.Manager):
    """
    To compute user's level in specified semester,
    level-up with maximum 'new_level' is retrieved from all level-ups before that semester.
    """

    def for_users_in_semester_as_dict(self, semester_pk, users_pks=None):
        """
        Returns a defaultdict {user_pk: level in requested semester (integer 1-4), default 1}.
        Needed for results calculation (fast indexing by user with only one DB query used).
        """
        if users_pks is None:
            users_level_ups = self
        else:
            users_level_ups = self.filter(user__pk__in=users_pks)

        max_level_ups = (
            users_level_ups.filter(last_semester_before_level_up__pk__lt=semester_pk)
            .values("user")
            .annotate(level=models.Max("new_level"))
        )

        levels_dict = defaultdict(lambda: 1)
        for level_up in max_level_ups:
            if level_up["level"] is not None:
                levels_dict[level_up["user"]] = level_up["level"]

        return levels_dict

    def for_user_in_semester(self, semester_pk, user_pk):
        """
        Returns a user level in the requested semester as an integer from range 1-4.
        Needed to access to a level of one user (e.g. in task list view).
        """
        return self.for_users_in_semester_as_dict(semester_pk, users_pks=[user_pk])[user_pk]


class KSPLevel(models.Model):
    """
    Camp attendance or good results in KSP semester can increase user's level as implemented in
    'ksp_levels.py'.

    One model instance keeps data about one level-up event for one user, storing new level
    explicitly.

    Since we might want to compute the new user level before the existence of the new semester model
    (e.g. if we want to display user's level for the next semester), we store the reference to the
    'last_semester_before_level_up' instead of the first semester in which user has this new level.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    new_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    source_semester = models.ForeignKey(
        Semester, blank=True, null=True, related_name="caused_level_ups", on_delete=models.CASCADE
    )
    source_camp = models.ForeignKey(Event, blank=True, null=True, on_delete=models.CASCADE)
    last_semester_before_level_up = models.ForeignKey(
        Semester, related_name="next_semester_level_ups", on_delete=models.CASCADE
    )

    objects = KSPLevelManager()

    def __str__(self):
        return "Level {} for {} after semester {}".format(
            self.new_level, self.user, self.last_semester_before_level_up
        )


class FKSLevelManager(models.Manager):
    """
    To compute user's level in specified semester,
    level-up with maximum 'new_level' is retrieved from all level-ups before that semester.
    """

    def for_users_in_semester_as_dict(self, semester_pk, users_pks=None):
        """
        Returns a defaultdict {user_pk: level in requested semester (integer 1-4), default 1}.
        Needed for results calculation (fast indexing by user with only one DB query used).
        """
        if users_pks is None:
            users_level_ups = self
        else:
            users_level_ups = self.filter(user__pk__in=users_pks)

        max_level_ups = (
            users_level_ups.filter(last_semester_before_level_up__pk__lt=semester_pk)
            .values("user")
            .annotate(level=models.Max("new_level"))
        )

        levels_dict = defaultdict(lambda: 1)
        for level_up in max_level_ups:
            if level_up["level"] is not None:
                levels_dict[level_up["user"]] = level_up["level"]

        return levels_dict

    def for_user_in_semester(self, semester_pk, user_pk):
        """
        Returns a user level in the requested semester as an integer from range 1-4.
        Needed to access to a level of one user (e.g. in task list view).
        """
        return self.for_users_in_semester_as_dict(semester_pk, users_pks=[user_pk])[user_pk]


class FKSLevel(models.Model):
    """
    Camp attendance or good results in FKS semester can increase user's level as implemented in
    'fks_levels.py'.

    One model instance keeps data about one level-up event for one user, storing new level
    explicitly.

    Since we might want to compute the new user level before the existence of the new semester model
    (e.g. if we want to display user's level for the next semester), we store the reference to the
    'last_semester_before_level_up' instead of the first semester in which user has this new level.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    new_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    source_semester = models.ForeignKey(
        Semester,
        blank=True,
        null=True,
        related_name="FKS_caused_level_ups",
        on_delete=models.CASCADE,
    )
    source_camp = models.ForeignKey(Event, blank=True, null=True, on_delete=models.CASCADE)
    last_semester_before_level_up = models.ForeignKey(
        Semester, related_name="FKS_next_semester_level_ups", on_delete=models.CASCADE
    )

    objects = FKSLevelManager()

    def __str__(self):
        return "Level {} for {} after semester {}".format(
            self.new_level, self.user, self.last_semester_before_level_up
        )
