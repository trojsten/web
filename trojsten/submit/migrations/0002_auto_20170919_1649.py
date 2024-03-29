# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-09-19 14:49
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("old_submit", "0001_squashed_0005_auto_20170303_1939")]

    operations = [
        migrations.AlterField(
            model_name="submit",
            name="testing_status",
            field=models.CharField(
                blank=True,
                choices=[
                    (b"reviewed", "reviewed"),
                    (b"in queue", "in queue"),
                    (b"finished", "finished"),
                ],
                max_length=128,
                verbose_name="stav testovania",
            ),
        ),
        migrations.AlterField(
            model_name="submit",
            name="time",
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name="\u010das"),
        ),
    ]
