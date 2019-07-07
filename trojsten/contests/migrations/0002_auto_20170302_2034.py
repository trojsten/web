# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-02 19:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0011_userpropertykey_hidden"),
        ("contests", "0001_squashed_0008_auto_20170228_2341"),
    ]

    operations = [
        migrations.AddField(
            model_name="competition",
            name="required_user_props",
            field=models.ManyToManyField(
                to="people.UserPropertyKey", verbose_name="Povinn\xe9 vlastnosti \u010dloveka"
            ),
        ),
        migrations.AlterField(
            model_name="round",
            name="solutions_visible",
            field=models.BooleanField(
                default=False, verbose_name="vidite\u013enos\u0165 vzor\xe1kov"
            ),
        ),
        migrations.AlterField(
            model_name="round",
            name="visible",
            field=models.BooleanField(default=False, verbose_name="vidite\u013enos\u0165"),
        ),
    ]
