# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Address(models.Model):
    street = models.CharField(max_length=70, verbose_name='ulica')
    town = models.CharField(max_length=64, db_index=True, verbose_name='mesto')
    postal_code = models.CharField(
        max_length=16, db_index=True, verbose_name='PSČ')
    country = models.CharField(
        max_length=32, db_index=True, verbose_name='krajina')

    def __str__(self):
        return (
            self.street + " " + self.number + ", " +
            self.town + ", " + self.postal_code + ", " +
            self.country)

    class Meta:
        verbose_name = 'Adresa'
        verbose_name_plural = 'Adresy'


@python_2_unicode_compatible
class School(models.Model):
    abbreviation = models.CharField(max_length=100,
                                    blank=True,
                                    verbose_name="skratka",
                                    help_text="Sktatka názvu školy.")
    verbose_name = models.CharField(max_length=100,
                                    verbose_name="celý názov")
    addr_name = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)

    class Meta:
        verbose_name = "škola"
        verbose_name_plural = "školy"
        ordering = ("city", "street", "verbose_name")

    def __str__(self):
        result = ""
        if self.abbreviation:
            result += self.abbreviation + ", "
        result += self.verbose_name
        if self.street:
            result += ", " + self.street
        if self.city or self.zip_code:
            result += ", "
        if self.zip_code:
            result += self.zip_code
        if self.city:
            result += " " + self.city
        return result



