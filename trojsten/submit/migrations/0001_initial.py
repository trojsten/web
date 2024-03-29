# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-08 08:51
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contests", "0003_category_task"),
    ]

    operations = [
        migrations.CreateModel(
            name="Submit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("time", models.DateTimeField(auto_now_add=True, verbose_name="\u010das")),
                (
                    "submit_type",
                    models.IntegerField(
                        choices=[
                            (0, b"source"),
                            (1, b"description"),
                            (2, b"testable_zip"),
                            (3, b"external"),
                        ],
                        verbose_name="typ submitu",
                    ),
                ),
                (
                    "points",
                    models.DecimalField(decimal_places=2, max_digits=5, verbose_name="body"),
                ),
                ("filepath", models.CharField(blank=True, max_length=128, verbose_name="s\xfabor")),
                (
                    "testing_status",
                    models.CharField(blank=True, max_length=128, verbose_name="stav testovania"),
                ),
                (
                    "tester_response",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "O\u010dak\xe1van\xe9 odpovede s\xfa OK, EXC, WA, SEC, TLE, IGN, CERR"
                        ),
                        max_length=10,
                        verbose_name="odpove\u010f testova\u010da",
                    ),
                ),
                (
                    "protocol_id",
                    models.CharField(
                        blank=True, max_length=128, verbose_name="\u010d\xedslo protokolu"
                    ),
                ),
                (
                    "reviewer_comment",
                    models.TextField(blank=True, verbose_name="koment\xe1r od opravovate\u013ea"),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contests.Task",
                        verbose_name="\xfaloha",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="odovzd\xe1vate\u013e",
                    ),
                ),
            ],
            options={"verbose_name": "Submit", "verbose_name_plural": "Submity"},
        )
    ]
