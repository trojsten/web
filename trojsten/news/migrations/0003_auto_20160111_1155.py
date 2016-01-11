# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20160110_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='slug',
            field=autoslug.fields.AutoSlugField(populate_from='title', unique=True, editable=False),
        ),
    ]
