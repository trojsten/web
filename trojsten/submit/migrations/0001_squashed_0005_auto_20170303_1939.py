# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-09 21:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [
        ("old_submit", "0001_initial"),
        ("old_submit", "0002_auto_20160608_1143"),
        ("old_submit", "0003_externalsubmittoken"),
        ("old_submit", "0004_auto_20170108_1728"),
        ("old_submit", "0005_auto_20170303_1939"),
    ]

    initial = True

    dependencies = [
        ("contests", "0003_category_task"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contests", "0006_auto_20160925_1324"),
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
                ("filepath", models.CharField(blank=True, max_length=512, verbose_name="s\xfabor")),
                (
                    "testing_status",
                    models.CharField(blank=True, max_length=128, verbose_name="stav testovania"),
                ),
                (
                    "tester_response",
                    models.CharField(
                        blank=True,
                        help_text="O\u010dak\xe1van\xe9 odpovede s\xfa CERR, TLE, WA, MLE, OK, IGN, SEC, EXC",
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
        ),
        migrations.CreateModel(
            name="ExternalSubmitToken",
            fields=[
                (
                    "token",
                    models.CharField(
                        max_length=40, primary_key=True, serialize=False, verbose_name="token"
                    ),
                ),
                ("name", models.CharField(max_length=64, verbose_name="n\xe1zov")),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contests.Task",
                        verbose_name="\xfaloha",
                    ),
                ),
            ],
        ),
    ]
