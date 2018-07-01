# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-07-01 21:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('old_submit', '0002_auto_20170919_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submit',
            name='tester_response',
            field=models.CharField(blank=True, help_text='O\u010dak\xe1van\xe9 odpovede s\xfa CERR, TLE, WA, MLE, OK, IGN, PROTCOR, SEC, EXC', max_length=10, verbose_name='odpove\u010f testova\u010da'),
        ),
        migrations.AlterField(
            model_name='submit',
            name='testing_status',
            field=models.CharField(blank=True, choices=[(b'reviewed', 'reviewed'), (b'in queue', 'in queue'), (b'finished', 'finished'), (b'OK', 'OK')], max_length=128, verbose_name='stav testovania'),
        ),
    ]
