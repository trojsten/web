# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-08 16:28
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("old_submit", "0003_externalsubmittoken")]

    operations = [
        migrations.AlterField(
            model_name="submit",
            name="filepath",
            field=models.CharField(blank=True, max_length=512, verbose_name="s\xfabor"),
        )
    ]
