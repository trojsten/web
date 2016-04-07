# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0002_auto_20160119_1100'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='repo',
        ),
        migrations.RemoveField(
            model_name='competition',
            name='repo_root',
        ),
        migrations.DeleteModel(
            name='Repository',
        ),
    ]
