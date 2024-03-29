# Generated by Django 2.2.13 on 2020-09-23 09:06

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contests", "0019_auto_20191212_1830"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="susi_big_hint",
            field=models.TextField(blank=True, default="", verbose_name="Suši velký hint"),
        ),
        migrations.AddField(
            model_name="task",
            name="susi_small_hint",
            field=models.TextField(blank=True, default="", verbose_name="Suši malý hint"),
        ),
        migrations.AddField(
            model_name="task",
            name="text_submit_solution",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    blank=True,
                    default="",
                    max_length=512,
                    verbose_name="textové riešenia (oddeľ čiarkou)",
                ),
                blank=True,
                default=list,
                size=None,
            ),
        ),
    ]
