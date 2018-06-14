from django.db import models


class DiplomaManager(models.Manager):
    pass


class Diploma(models.Model):
    objects = DiplomaManager()