# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-27 10:28
from __future__ import unicode_literals

from datetime import date

from django.conf import settings
from django.db import migrations, models
import django.utils.timezone

from trojsten.people.constants import OTHER_SCHOOL_ID


def migrate_schools(apps, schema_editor):
    User = apps.get_model('people', 'User')
    UserSchool = apps.get_model('people', 'UserSchool')
    for user in User.objects.all():
        if user.school and user.school.id != OTHER_SCHOOL_ID:
            UserSchool.objects.create(
                user=user,
                school=user.school,
                start_time=date(max(user.graduation - 8, 1) if user.graduation else 1, 9, 1)
            )


def reverse_migrate_schools(apps, schema_editor):
    UserSchool = apps.get_model('people', 'UserSchool')
    for row in UserSchool.objects.order_by('user', '-start_time').distinct('user'):
        row.user.school = row.school
        row.user.save()


class Migration(migrations.Migration):

    replaces = [('people', '0017_auto_20180607_1156'), ('people', '0018_auto_20180607_1158'), ('people', '0019_auto_20180608_2124')]

    dependencies = [
        ('schools', '0001_initial'),
        ('people', '0016_merge_20180121_1616'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSchool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateField(verbose_name='Start of study')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schools.School', verbose_name='School')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.RunPython(
            code=migrate_schools,
            reverse_code=reverse_migrate_schools,
        ),
        migrations.RemoveField(
            model_name='user',
            name='school',
        ),
        migrations.AlterField(
            model_name='userschool',
            name='start_time',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Start of study'),
        ),
    ]
