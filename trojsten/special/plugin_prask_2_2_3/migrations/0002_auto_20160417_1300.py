# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('plugin_prask_2_2_3', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlink',
            name='user',
            field=models.OneToOneField(related_name='+', null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
