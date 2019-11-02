# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="n\xe1zov")),
                ("start_time", models.DateTimeField(verbose_name="\u010das za\u010diatku")),
                ("end_time", models.DateTimeField(verbose_name="\u010das konca")),
                (
                    "registration_deadline",
                    models.DateTimeField(
                        null=True, verbose_name="deadline pre registr\xe1ciu", blank=True
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        default="",
                        help_text='Obsah bude prehnan\xfd <a href="http://en.wikipedia.org/wiki/Markdown">Markdownom</a>.',
                        blank=True,
                    ),
                ),
            ],
            options={
                "ordering": ["-end_time", "-start_time"],
                "verbose_name": "akcia",
                "verbose_name_plural": "akcie",
            },
        ),
        migrations.CreateModel(
            name="EventType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="n\xe1zov")),
                ("is_camp", models.BooleanField(verbose_name="s\xfastredko")),
            ],
            options={"verbose_name": "typ akcie", "verbose_name_plural": "typy akci\xed"},
        ),
        migrations.CreateModel(
            name="Invitation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "type",
                    models.SmallIntegerField(
                        default=0,
                        verbose_name="typ pozv\xe1nky",
                        choices=[
                            (0, "\xfa\u010dastn\xedk"),
                            (1, "n\xe1hradn\xedk"),
                            (2, "ved\xfaci"),
                        ],
                    ),
                ),
                ("going", models.NullBooleanField(verbose_name="z\xfa\u010dastn\xed sa")),
            ],
            options={"verbose_name": "pozv\xe1nka", "verbose_name_plural": "pozv\xe1nky"},
        ),
        migrations.CreateModel(
            name="Link",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("title", models.CharField(max_length=100, verbose_name="titulok")),
                ("name", models.CharField(max_length=300, verbose_name="meno")),
                ("url", models.URLField(max_length=300)),
            ],
            options={"verbose_name": "odkaz", "verbose_name_plural": "odkazy"},
        ),
        migrations.CreateModel(
            name="Place",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="n\xe1zov")),
            ],
            options={"verbose_name": "miesto akcie", "verbose_name_plural": "miesta akci\xed"},
        ),
        migrations.CreateModel(
            name="Registration",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="n\xe1zov")),
                (
                    "text",
                    models.TextField(
                        help_text='Obsah bude prehnan\xfd <a href="http://en.wikipedia.org/wiki/Markdown">Markdownom</a>.'
                    ),
                ),
            ],
            options={
                "verbose_name": "Prihl\xe1\u0161ka",
                "verbose_name_plural": "Prihl\xe1\u0161ky",
            },
        ),
    ]
