# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-15 15:08
from __future__ import unicode_literals

import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("people", "0016_merge_20180121_1616")]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="graduation",
            field=models.IntegerField(
                help_text="Required field for students.", null=True, verbose_name="rok maturity"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="school",
            field=models.ForeignKey(
                blank=True,
                default=None,
                help_text='Type an abbreviation, part of the name or school address and select the correct option from the list. If your school is not in the list, pick "Other school" and send us an e-mail',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="schools.School",
                verbose_name="škola",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                blank=True,
                error_messages={"unique": "A user with that username already exists."},
                help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                max_length=150,
                unique=True,
                validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                verbose_name="username",
            ),
        ),
    ]
