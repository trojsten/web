# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-03 18:47
import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("people", "0011_auto_20170218_1724")]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="country",
            field=django_countries.fields.CountryField(max_length=2),
        )
    ]
