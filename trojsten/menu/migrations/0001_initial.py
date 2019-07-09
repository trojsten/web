# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
import sortedm2m.fields
from django.db import migrations, models

import trojsten.menu.models


class Migration(migrations.Migration):

    dependencies = [("sites", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="MenuGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Zobraz\xed sa v menu pre v\u0161etky skupiny okrem prvej.",
                        max_length=64,
                        verbose_name="n\xe1zov",
                    ),
                ),
                (
                    "staff_only",
                    models.BooleanField(default=False, verbose_name="iba pre ved\xfacich"),
                ),
                ("position", models.IntegerField(verbose_name="poz\xedcia")),
            ],
            options={"verbose_name": "Skupina v menu", "verbose_name_plural": "Skupina v menu"},
        ),
        migrations.CreateModel(
            name="MenuItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("name", models.CharField(max_length=64, verbose_name="n\xe1zov")),
                (
                    "url",
                    models.CharField(
                        help_text='Povolen\xe9 tvary s\xfa "http(s)://domain.com/path", "/absolute/path" a "@urlname".',
                        max_length=196,
                        verbose_name="adresa",
                        validators=[trojsten.menu.models.validate_url],
                    ),
                ),
                ("glyphicon", models.CharField(max_length=64, verbose_name="glyphicon")),
                (
                    "active_url_pattern",
                    models.CharField(
                        help_text="Medzerou oddelen\xe9 urlnames a regul\xe1rne v\xfdrazy,ktor\xe9 pri zhode s cestou zv\xfdraznia aktu\xe1lnu polo\u017eku.",
                        max_length=196,
                        verbose_name="regul\xe1rne v\xfdrazy pre zv\xfdraznenie",
                        blank=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Polo\u017eka v menu",
                "verbose_name_plural": "Polo\u017eky v menu",
            },
        ),
        migrations.AddField(
            model_name="menugroup",
            name="items",
            field=sortedm2m.fields.SortedManyToManyField(
                help_text=None,
                related_name="groups",
                verbose_name="polo\u017eky",
                to="menu.MenuItem",
            ),
        ),
        migrations.AddField(
            model_name="menugroup",
            name="site",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="menu_groups",
                verbose_name="str\xe1nka",
                to="sites.Site",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="menugroup", unique_together=set([("position", "site")])
        ),
    ]
