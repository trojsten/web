# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import date

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import python_2_unicode_compatible
import django.utils.timezone


@python_2_unicode_compatible
class Address(models.Model):
    street = models.CharField(max_length=64, verbose_name='ulica')
    number = models.CharField(max_length=16, verbose_name='číslo')
    town = models.CharField(max_length=64, db_index=True, verbose_name='mesto')
    postal_code = models.CharField(max_length=16, db_index=True, verbose_name='PSČ')
    country = models.CharField(max_length=32, db_index=True, verbose_name='krajina')
    # lives_here <- related name to Person.home_address

    def __str__(self):
        return (
            self.street + " " + self.number + ", " +
            self.town + ", " + self.postal_code + ", " +
            self.country)

    class Meta:
        verbose_name = 'Adresa'
        verbose_name_plural = 'Adresy'


@python_2_unicode_compatible
class Person(models.Model):
    '''
    Holds, provide access to or manages all informations
    related to a person.
    '''
    name = models.CharField(
        max_length=128,  db_index=True, verbose_name='meno')
    surname = models.CharField(
        max_length=128,  db_index=True, verbose_name='priezvisko')
    birth_date = models.DateField(
        db_index=True, verbose_name='dátum narodenia')
    home_address = models.ForeignKey(Address,
                                     related_name='lives_here',
                                     null=True,
                                     verbose_name='domáca adresa')
    correspondence_address = models.ForeignKey(Address,
                                               related_name='accepting_mails_here',
                                               null=True,
                                               verbose_name='adresa korešpondencie')
    email = models.EmailField(verbose_name='e-mail')
    
    def __str__(self):
        return '%s %s' % (self.name, self.surname)

    class Meta:
        verbose_name = 'Osoba'
        verbose_name_plural = 'Ľudia'
