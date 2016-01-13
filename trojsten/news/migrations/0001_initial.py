# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='publication date')),
                ('title', models.CharField(max_length=100)),
                ('text', models.TextField(help_text='Obsah bude prehnan\xfd <a href="http://en.wikipedia.org/wiki/Markdown">Markdownom</a>.')),
                ('slug', autoslug.fields.AutoSlugField(populate_from='title', unique=True, editable=False)),
            ],
            options={
                'ordering': ('-pub_date',),
                'get_latest_by': 'pub_date',
                'verbose_name': 'novinka',
                'verbose_name_plural': 'novinky',
            },
        ),
    ]
