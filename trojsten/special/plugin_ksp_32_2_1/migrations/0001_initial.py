# -*- coding: utf-8 -*-
import django
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Try",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("input", models.CharField(max_length=15)),
                ("output", models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name="UserLevel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("level_id", models.IntegerField()),
                ("try_count", models.IntegerField(default=0)),
                ("solved", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="try",
            name="userlevel",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="plugin_ksp_32_2_1.UserLevel"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="userlevel", unique_together=set([("user", "level_id")])
        ),
    ]
