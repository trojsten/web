# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='n\xe1zov')),
                ('repo_root', models.CharField(max_length=128, verbose_name='adresa foldra s\xfa\u0165a\u017ee v repozit\xe1ri')),
                ('primary_school_only', models.BooleanField(default=False, verbose_name='s\xfa\u0165a\u017e je iba pre z\xe1klado\u0161kol\xe1kov')),
                ('organizers_group', models.ForeignKey(verbose_name='skupina ved\xfacich', to='auth.Group', null=True)),
            ],
            options={
                'verbose_name': 'S\xfa\u0165a\u017e',
                'verbose_name_plural': 'S\xfa\u0165a\u017ee',
            },
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('notification_string', models.UUIDField(primary_key=True, serialize=False, editable=False, max_length=32, blank=True, unique=True, verbose_name='string pre push notifik\xe1ciu')),
                ('url', models.CharField(max_length=128, verbose_name='url git repozit\xe1ra')),
            ],
            options={
                'verbose_name': 'Repozit\xe1r',
                'verbose_name_plural': 'Repozit\xe1re',
            },
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField(verbose_name='\u010d\xedslo')),
                ('start_time', models.DateTimeField(default=datetime.datetime(2016, 1, 18, 0, 0), verbose_name='za\u010diatok')),
                ('end_time', models.DateTimeField(default=datetime.datetime(2016, 1, 18, 23, 59, 59), verbose_name='koniec')),
                ('visible', models.BooleanField(verbose_name='vidite\u013enos\u0165')),
                ('solutions_visible', models.BooleanField(verbose_name='vidite\u013enos\u0165 vzor\xe1kov')),
            ],
            options={
                'verbose_name': 'Kolo',
                'verbose_name_plural': 'Kol\xe1',
            },
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='n\xe1zov', blank=True)),
                ('number', models.IntegerField(verbose_name='\u010d\xedslo s\xe9rie')),
                ('year', models.IntegerField(verbose_name='ro\u010dn\xedk')),
                ('competition', models.ForeignKey(verbose_name='s\xfa\u0165a\u017e', to='contests.Competition')),
            ],
            options={
                'verbose_name': 'S\xe9ria',
                'verbose_name_plural': 'S\xe9rie',
            },
        ),
        migrations.AddField(
            model_name='round',
            name='series',
            field=models.ForeignKey(verbose_name='s\xe9ria', to='contests.Series'),
        ),
        migrations.AddField(
            model_name='competition',
            name='repo',
            field=models.ForeignKey(verbose_name='git repozit\xe1r', blank=True, to='contests.Repository', null=True),
        ),
        migrations.AddField(
            model_name='competition',
            name='sites',
            field=models.ManyToManyField(to='sites.Site'),
        ),
    ]
