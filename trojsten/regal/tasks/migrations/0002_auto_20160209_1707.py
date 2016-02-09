# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submit',
            name='tester_response',
            field=models.CharField(help_text='O\u010dak\xe1van\xe9 odpovede s\xfa OK, EXC, WA, SEC, TLE, CERR', max_length=10, verbose_name='odpove\u010f testova\u010da', blank=True),
        ),
    ]
