# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-16 14:29
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("people", "0007_auto_20160607_1400")]

    operations = [
        migrations.AddField(
            model_name="userpropertykey",
            name="regex",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name="regul\xe1rny v\xfdraz pre hodnotu",
            ),
        )
    ]
