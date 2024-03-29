# -*- coding: utf-8 -*-
import django
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="UserLink",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("link", models.URLField(unique=True, max_length=255)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        null=True,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        unique=True,
                    ),
                ),
            ],
        )
    ]
