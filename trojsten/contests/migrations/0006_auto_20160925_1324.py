# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-25 11:24
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("contests", "0005_auto_20160910_1317")]

    operations = [
        migrations.AlterModelOptions(
            name="semester",
            options={"verbose_name": "\u010cas\u0165", "verbose_name_plural": "\u010casti"},
        ),
        migrations.AlterField(
            model_name="round",
            name="semester",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="contests.Semester",
                verbose_name="\u010das\u0165",
            ),
        ),
        migrations.AlterField(
            model_name="semester",
            name="number",
            field=models.IntegerField(verbose_name="\u010d\xedslo \u010d\xe1sti"),
        ),
    ]
