# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='round',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 11, 23, 59, 59), verbose_name='koniec'),
        ),
        migrations.AlterField(
            model_name='round',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 11, 0, 0), verbose_name='za\u010diatok'),
        ),
    ]
