# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(max_length=1)),
                ('points', models.IntegerField(default=0)),
                ('state', models.CharField(default=b'', max_length=256)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+',
                                           to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField()),
                ('response', models.IntegerField()),
                ('user_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visits',
                                                    to='plugin_prask_1_2_1.UserCategory')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='usercategory',
            unique_together=set([('user', 'category')]),
        ),
    ]
