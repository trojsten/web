# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import trojsten.utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='round',
            name='end_time',
            field=models.DateTimeField(default=trojsten.utils.utils.default_end_time, verbose_name='koniec'),
        ),
        migrations.AlterField(
            model_name='round',
            name='start_time',
            field=models.DateTimeField(default=trojsten.utils.utils.default_start_time, verbose_name='za\u010diatok'),
        ),
    ]
