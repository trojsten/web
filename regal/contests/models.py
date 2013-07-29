from django.db import models
from datetime import datetime

class Contest(models.Model):
    name = models.CharField(max_length = 128)
    informatics = models.BooleanField()
    math = models.BooleanField()
    physics = models.BooleanField()

class Year(models.Model):
    name = models.CharField(max_length = 128)
    year = models.IntegerField()

class Round(models.Model):
    number = models.IntegerField()
    end_time = models.DateTimeField()
    visibility = models.IntegerField()
    

class Task(models.Model):
    name = models.CharField(max_length = 128)
    number = models.IntegerField()
