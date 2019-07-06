# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("sites", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Thread",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                ("sites", models.ManyToManyField(to="sites.Site")),
            ],
            options={
                "verbose_name": "diskusn\xe9 vl\xe1kno",
                "verbose_name_plural": "diskusn\xe9 vl\xe1kna",
            },
        )
    ]
