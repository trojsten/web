# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-08 08:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_auto_20160608_1051'),
        ('submit', '0001_initial'),
    ]

    state_operations = [
        migrations.DeleteModel(
            name='Submit',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
