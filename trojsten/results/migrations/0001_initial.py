# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('people', '0001_initial'),
        ('contests', '0001_squashed_0003_auto_20160301_1436'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrozenPoints',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description_points', models.CharField(max_length=10, verbose_name='body za popis')),
                ('source_points', models.CharField(max_length=10, verbose_name='body za program')),
                ('sum', models.CharField(max_length=10, verbose_name='body')),
                ('task', models.ForeignKey(verbose_name='\xfaloha', to='tasks.Task')),
            ],
            options={
                'verbose_name': 'Zmrazen\xe9 body za \xfalohu',
                'verbose_name_plural': 'Zmrazen\xe9 body za \xfalohy',
            },
        ),
        migrations.CreateModel(
            name='FrozenResults',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_single_round', models.BooleanField(verbose_name='vynecha\u0165 predo\u0161l\xe9 kol\xe1')),
                ('has_previous_results', models.BooleanField(default=False, verbose_name='zah\u0155\u0148a predo\u0161l\xe9 kol\xe1')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='\u010das')),
                ('category', models.ForeignKey(verbose_name='kateg\xf3ria', blank=True, to='tasks.Category', null=True)),
                ('round', models.ForeignKey(verbose_name='kolo', to='contests.Round')),
            ],
            options={
                'verbose_name': 'Zmrazen\xe1 v\xfdsledkovka',
                'verbose_name_plural': 'Zmrazen\xe9 v\xfdsledkovky',
            },
        ),
        migrations.CreateModel(
            name='FrozenUserResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rank', models.IntegerField(verbose_name='poradie')),
                ('prev_rank', models.IntegerField(null=True, verbose_name='poradie', blank=True)),
                ('fullname', models.CharField(max_length=500, verbose_name='pln\xe9 meno')),
                ('school_year', models.IntegerField(verbose_name='ro\u010dn\xedk')),
                ('previous_points', models.CharField(max_length=10, verbose_name='body z predo\u0161l\xfdch k\xf4l')),
                ('sum', models.CharField(max_length=10, verbose_name='suma')),
                ('frozenresults', models.ForeignKey(verbose_name='v\xfdsledkovka', to='results.FrozenResults')),
                ('original_user', models.ForeignKey(verbose_name='p\xf4vodn\xfd pou\u017e\xedvate\u013e', to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(verbose_name='\u0161kola', to='people.School')),
                ('task_points', models.ManyToManyField(to='results.FrozenPoints', verbose_name='body za \xfalohy')),
            ],
            options={
                'verbose_name': 'Zmrazen\xfd v\xfdsledok',
                'verbose_name_plural': 'Zmrazen\xe9 v\xfdsledky',
            },
        ),
    ]
