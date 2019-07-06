# -*- coding: utf-8 -*-

# FIXME(generic_results_stage_2): Those are old, unsupported frozen results.
# Create new frozen result models and, probably, throw the old models and data out.


from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.postgres.fields import JSONField


@python_2_unicode_compatible
class FrozenResults(models.Model):
    round = models.ForeignKey("contests.Round", verbose_name="kolo", on_delete=models.CASCADE)
    is_single_round = models.BooleanField(verbose_name="vynechať predošlé kolá")
    has_previous_results = models.BooleanField(default=False, verbose_name="zahŕňa predošlé kolá")
    category = models.ForeignKey(
        "contests.Category",
        blank=True,
        null=True,
        verbose_name="kategória",
        on_delete=models.CASCADE,
    )
    time = models.DateTimeField(auto_now_add=True, verbose_name="čas")

    class Meta:
        verbose_name = "Zmrazená výsledkovka"
        verbose_name_plural = "Zmrazené výsledkovky"

    def __str__(self):
        return "%s(%s) [%s]" % (
            self.round,
            "single" if self.is_single_round else "multi",
            self.category,
        )


@python_2_unicode_compatible
class FrozenPoints(models.Model):
    task = models.ForeignKey("contests.Task", verbose_name="úloha", on_delete=models.CASCADE)
    description_points = models.CharField(max_length=10, verbose_name="body za popis")
    source_points = models.CharField(max_length=10, verbose_name="body za program")
    sum = models.CharField(max_length=10, verbose_name="body")

    class Meta:
        verbose_name = "Zmrazené body za úlohu"
        verbose_name_plural = "Zmrazené body za úlohy"

    def __str__(self):
        return "%s: Popis: %s, Program: %s" % (
            self.task,
            self.description_points,
            self.source_points,
        )


@python_2_unicode_compatible
class FrozenUserResult(models.Model):
    frozenresults = models.ForeignKey(
        "FrozenResults", verbose_name="výsledkovka", on_delete=models.CASCADE
    )
    original_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="pôvodný používateľ", on_delete=models.CASCADE
    )
    rank = models.IntegerField(verbose_name="poradie")
    prev_rank = models.IntegerField(verbose_name="poradie", blank=True, null=True)
    fullname = models.CharField(max_length=500, verbose_name="plné meno")
    school_year = models.IntegerField(verbose_name="ročník")
    school = models.ForeignKey(
        "schools.School", verbose_name="škola", null=True, on_delete=models.CASCADE
    )
    previous_points = models.CharField(max_length=10, verbose_name="body z predošlých kôl")
    sum = models.CharField(max_length=10, verbose_name="suma")
    task_points = models.ManyToManyField(FrozenPoints, verbose_name="body za úlohy")

    class Meta:
        verbose_name = "Zmrazený výsledok"
        verbose_name_plural = "Zmrazené výsledky"

    def __str__(self):
        return "%s %s" % (self.frozenresults, self.fullname)


@python_2_unicode_compatible
class Results(models.Model):
    round = models.ForeignKey("contests.Round", verbose_name="kolo", on_delete=models.CASCADE)
    tag = models.CharField(max_length=50, blank=True, null=True, verbose_name="tag/kategória")
    is_single_round = models.BooleanField(verbose_name="vynechať predošlé kolá")
    has_previous_results = models.BooleanField(default=False, verbose_name="zahŕňa predošlé kolá")
    time = models.DateTimeField(auto_now_add=True, verbose_name="čas")
    serialized_results = JSONField(blank=True)

    class Meta:
        verbose_name = "Výsledkovka"
        verbose_name_plural = "Výsledkovky"
        indexes = [models.Index(fields=["round", "tag", "is_single_round"])]
        unique_together = ("round", "tag", "is_single_round")

    def __str__(self):
        return "%s(%s) [%s]" % (self.round, "single" if self.is_single_round else "multi", self.tag)
