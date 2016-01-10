# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=16, verbose_name='n\xe1zov')),
                ('competition', models.ForeignKey(verbose_name='s\xfa\u0165a\u017e', to='contests.Competition')),
            ],
            options={
                'verbose_name': 'Kateg\xf3ria',
                'verbose_name_plural': 'Kateg\xf3rie',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Submit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='\u010das')),
                ('submit_type', models.IntegerField(verbose_name='typ submitu', choices=[(0, 'source'), (1, 'description'), (2, 'testable_zip'), (3, 'external')])),
                ('points', models.DecimalField(verbose_name='body', max_digits=5, decimal_places=2)),
                ('filepath', models.CharField(max_length=128, verbose_name='s\xfabor', blank=True)),
                ('testing_status', models.CharField(max_length=128, verbose_name='stav testovania', blank=True)),
                ('tester_response', models.CharField(max_length=10, verbose_name='odpove\u010f testova\u010da', blank=True)),
                ('protocol_id', models.CharField(max_length=128, verbose_name='\u010d\xedslo protokolu', blank=True)),
            ],
            options={
                'verbose_name': 'Submit',
                'verbose_name_plural': 'Submity',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='n\xe1zov')),
                ('number', models.IntegerField(verbose_name='\u010d\xedslo')),
                ('description_points', models.IntegerField(verbose_name='body za popis')),
                ('source_points', models.IntegerField(verbose_name='body za program')),
                ('integer_source_points', models.BooleanField(default=True, verbose_name='celo\u010d\xedseln\xe9 body za program')),
                ('has_source', models.BooleanField(verbose_name='odovz\xe1va sa zdroj\xe1k')),
                ('has_description', models.BooleanField(verbose_name='odovz\xe1va sa popis')),
                ('has_testablezip', models.BooleanField(default=False, verbose_name='odovzd\xe1va sa zip na testova\u010d')),
                ('external_submit_link', models.CharField(max_length=128, null=True, verbose_name='Odkaz na extern\xe9 odovzd\xe1vanie', blank=True)),
                ('category', models.ManyToManyField(to='tasks.Category', verbose_name='kateg\xf3ria', blank=True)),
                ('reviewer', models.ForeignKey(verbose_name='opravovate\u013e', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('round', models.ForeignKey(verbose_name='kolo', to='contests.Round')),
            ],
            options={
                'verbose_name': '\xdaloha',
                'verbose_name_plural': '\xdalohy',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='submit',
            name='task',
            field=models.ForeignKey(verbose_name='\xfaloha', to='tasks.Task'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submit',
            name='user',
            field=models.ForeignKey(verbose_name='odovzd\xe1vate\u013e', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
