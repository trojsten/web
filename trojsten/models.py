# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from regal.people.models import Address, School


class User(AbstractUser):
    '''
    Holds, provide access to or manages all informations
    related to a person.
    '''
    birth_date = models.DateField(
        null=True, db_index=True, verbose_name='dátum narodenia')
    home_address = models.ForeignKey(Address,
                                     related_name='lives_here',
                                     null=True,
                                     verbose_name='domáca adresa')
    mailing_address = models.ForeignKey(Address,
                                        related_name='accepting_mails_here',
                                        null=True,
                                        verbose_name='adresa korešpondencie')
    school = models.ForeignKey(School,
                               null=True,
                               default=1,
                               verbose_name="škola",
                               help_text='Do políčka napíšte skratku, '
                               'časť názvu alebo adresy školy a následne '
                               'vyberte správnu možnosť zo zoznamu. '
                               'Pokiaľ vaša škola nie je '
                               'v&nbsp;zozname, vyberte "Gymnázium iné" '
                               'a&nbsp;pošlite nám e-mail.')
    graduation = models.IntegerField(blank=True, null=True,
                                     verbose_name="rok maturity",
                                     help_text="Povinné pre žiakov.")

    class Meta:
        verbose_name = "používateľ"
        verbose_name_plural = "používatelia"
