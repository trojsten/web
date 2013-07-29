# -*- coding: utf-8 -*- 
from django.db import models
from datetime import datetime

class Contest(models.Model):
    """ Contest consists of years.
    """
    name = models.CharField(max_length = 128)
    informatics = models.BooleanField()
    math = models.BooleanField()
    physics = models.BooleanField()

    def __unicode__(self):
        return self.name

class Year(models.Model):
    """ Year consits of several rounds.
    """
    contest = models.ForeignKey(Contest)
    number = models.IntegerField()
    year = models.IntegerField()

    def __unicode__(self):
        return str(self.number)+u'. ročník '+self.contest.__unicode__()

class Round(models.Model):
    """ Round has tasks.
        Holds informations about deadline and such things
    """
    year = models.ForeignKey(Year)
    number = models.IntegerField()
    end_time = models.DateTimeField()
    visible = models.BooleanField()

    def __unicode__(self):
        return str(self.number)+'. kolo'

class Task(models.Model):
    '''
    '''
    name = models.CharField(max_length = 128)
    number = models.IntegerField()

    def __unicode__(self):
        return name;
